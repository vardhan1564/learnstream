package com.learnsstream.service;

import com.learnsstream.dto.MiscDtos.*;
import com.learnsstream.entity.Course;
import com.learnsstream.entity.Enrollment;
import com.learnsstream.entity.Payment;
import com.learnsstream.entity.User;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.EnrollmentRepository;
import com.learnsstream.repository.PaymentRepository;
import com.learnsstream.repository.UserRepository;
import com.learnsstream.security.AuthUser;
import com.stripe.Stripe;
import com.stripe.exception.SignatureVerificationException;
import com.stripe.exception.StripeException;
import com.stripe.model.Event;
import com.stripe.model.StripeObject;
import com.stripe.model.checkout.Session;
import com.stripe.net.Webhook;
import com.stripe.param.checkout.SessionCreateParams;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Stripe Checkout. The price always comes from the database (never from the browser), and
 * enrollment happens only after Stripe confirms the session is paid - either via
 * POST /api/payments/verify (when the student returns) or via the webhook.
 */
@Service
public class PaymentService {

    private static final Logger log = LoggerFactory.getLogger(PaymentService.class);

    private final PaymentRepository paymentRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository;
    private final CourseService courseService;
    private final EnrollmentService enrollmentService;

    @Value("${stripe.api.key:}")
    private String stripeKey;

    @Value("${stripe.webhook.secret:}")
    private String webhookSecret;

    @Value("${stripe.currency:inr}")
    private String currency;

    @Value("${learnstream.frontend-url}")
    private String frontendUrl;

    public PaymentService(PaymentRepository paymentRepository, EnrollmentRepository enrollmentRepository,
                          UserRepository userRepository, CourseService courseService,
                          EnrollmentService enrollmentService) {
        this.paymentRepository = paymentRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.userRepository = userRepository;
        this.courseService = courseService;
        this.enrollmentService = enrollmentService;
    }

    @PostConstruct
    void init() {
        if (stripeKey != null && !stripeKey.isBlank()) {
            Stripe.apiKey = stripeKey;
        } else {
            log.warn("stripe.api.key is not set - paid checkout is disabled (free courses and rewards still work).");
        }
    }

    @Transactional
    public CheckoutResponse createCheckout(Long courseId, AuthUser viewer) {
        if (stripeKey == null || stripeKey.isBlank()) {
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "Online payments are not configured yet. Please contact the admin.");
        }
        Course course = courseService.requireCourse(courseId);
        if (!course.isPublished()) {
            throw ApiException.notFound("Course");
        }
        if (course.isFree()) {
            throw ApiException.badRequest("This course is free - just click Enroll.");
        }
        if (enrollmentRepository.existsByUserIdAndCourseId(viewer.id(), courseId)) {
            throw ApiException.conflict("You're already enrolled in this course");
        }
        User user = userRepository.findById(viewer.id()).orElseThrow(() -> ApiException.notFound("User"));
        long amount = Math.round(course.getPrice() * 100); // rupees -> paise

        SessionCreateParams params = SessionCreateParams.builder()
                .setMode(SessionCreateParams.Mode.PAYMENT)
                .setSuccessUrl(frontendUrl + "/payment-success?session_id={CHECKOUT_SESSION_ID}")
                .setCancelUrl(frontendUrl + "/courses/" + courseId + "?payment=cancelled")
                .setCustomerEmail(user.getEmail())
                .setClientReferenceId(String.valueOf(user.getId()))
                .putMetadata("userId", String.valueOf(user.getId()))
                .putMetadata("courseId", String.valueOf(courseId))
                .addLineItem(SessionCreateParams.LineItem.builder()
                        .setQuantity(1L)
                        .setPriceData(SessionCreateParams.LineItem.PriceData.builder()
                                .setCurrency(currency)
                                .setUnitAmount(amount)
                                .setProductData(SessionCreateParams.LineItem.PriceData.ProductData.builder()
                                        .setName(course.getTitle())
                                        .build())
                                .build())
                        .build())
                .build();
        try {
            Session session = Session.create(params);
            Payment payment = new Payment();
            payment.setUser(user);
            payment.setCourse(course);
            payment.setStripeSessionId(session.getId());
            payment.setAmount(amount);
            payment.setCurrency(currency);
            paymentRepository.save(payment);
            return new CheckoutResponse(session.getUrl());
        } catch (StripeException e) {
            log.error("Stripe checkout failed: {}", e.getMessage());
            throw new ApiException(HttpStatus.BAD_GATEWAY, "Payment provider error: " + e.getMessage());
        }
    }

    /** Called by the success page. Only the student who started the payment can confirm it. */
    @Transactional
    public VerifyPaymentResponse verify(String sessionId, AuthUser viewer) {
        Payment payment = paymentRepository.lockBySessionId(sessionId)
                .orElseThrow(() -> ApiException.notFound("Payment"));
        if (!payment.getUser().getId().equals(viewer.id())) {
            throw ApiException.notFound("Payment");
        }
        fulfil(payment);
        Course course = payment.getCourse();
        return new VerifyPaymentResponse(course.getId(), course.getTitle(), true);
    }

    @Transactional
    public void handleWebhook(String payload, String signature) {
        if (webhookSecret == null || webhookSecret.isBlank()) {
            throw ApiException.notFound("Webhook");
        }
        Event event;
        try {
            event = Webhook.constructEvent(payload, signature, webhookSecret);
        } catch (SignatureVerificationException e) {
            throw ApiException.badRequest("Invalid signature");
        } catch (RuntimeException e) {
            throw ApiException.badRequest("Malformed webhook payload");
        }
        if (!"checkout.session.completed".equals(event.getType())
                && !"checkout.session.async_payment_succeeded".equals(event.getType())) {
            return;
        }
        StripeObject obj = event.getDataObjectDeserializer().getObject().orElse(null);
        if (obj == null) {
            try {
                obj = event.getDataObjectDeserializer().deserializeUnsafe();
            } catch (Exception e) {
                log.warn("Could not read Stripe webhook payload: {}", e.getMessage());
                return;
            }
        }
        if (obj instanceof Session session) {
            paymentRepository.lockBySessionId(session.getId()).ifPresent(p -> {
                try {
                    fulfil(p);
                } catch (ApiException ex) {
                    log.info("Webhook: session {} not fulfilled: {}", session.getId(), ex.getMessage());
                }
            });
        }
    }

    @Transactional(readOnly = true)
    public List<PaymentView> recentPayments(int limit) {
        return paymentRepository.findRecentPaid(PageRequest.of(0, Math.min(Math.max(limit, 1), 200))).stream()
                .map(p -> new PaymentView(p.getId(), p.getUser().getFullName(), p.getUser().getEmail(),
                        p.getCourse().getTitle(), p.getAmount() / 100.0, p.getCurrency(), p.getPaidAt()))
                .toList();
    }

    /** Asks Stripe whether the session is paid; if so, marks the payment PAID and enrolls (idempotent). */
    private void fulfil(Payment payment) {
        if (Payment.STATUS_PAID.equals(payment.getStatus())) {
            enrollmentService.enroll(payment.getUser(), payment.getCourse(), Enrollment.SOURCE_PAID);
            return;
        }
        Session session;
        try {
            session = Session.retrieve(payment.getStripeSessionId());
        } catch (StripeException e) {
            log.error("Stripe lookup failed: {}", e.getMessage());
            throw new ApiException(HttpStatus.BAD_GATEWAY, "Could not confirm the payment with Stripe. Please refresh in a moment.");
        }
        boolean paid = "paid".equals(session.getPaymentStatus())
                || "no_payment_required".equals(session.getPaymentStatus());
        boolean amountOk = session.getAmountTotal() != null && session.getAmountTotal() >= payment.getAmount();
        String metaCourse = session.getMetadata() == null ? null : session.getMetadata().get("courseId");
        boolean courseOk = String.valueOf(payment.getCourse().getId()).equals(metaCourse);

        if (!paid) {
            throw new ApiException(HttpStatus.PAYMENT_REQUIRED, "Payment is not completed yet.");
        }
        if (!amountOk || !courseOk) {
            log.error("Stripe session {} does not match payment record {}", session.getId(), payment.getId());
            throw ApiException.badRequest("Payment details do not match. Please contact support.");
        }
        payment.setStatus(Payment.STATUS_PAID);
        payment.setPaidAt(LocalDateTime.now());
        paymentRepository.save(payment);
        enrollmentService.enroll(payment.getUser(), payment.getCourse(), Enrollment.SOURCE_PAID);
    }
}
