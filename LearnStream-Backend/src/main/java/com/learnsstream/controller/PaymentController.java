package com.learnsstream.controller;

import com.learnsstream.dto.MiscDtos.VerifyPaymentRequest;
import com.learnsstream.dto.MiscDtos.VerifyPaymentResponse;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.PaymentService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    /** Called by the frontend success page with the Stripe session id. */
    @PostMapping("/verify")
    public VerifyPaymentResponse verify(@Valid @RequestBody VerifyPaymentRequest req) {
        return paymentService.verify(req.sessionId(), CurrentUser.get());
    }

    /** Stripe -> server notification (configure stripe.webhook.secret to enable). */
    @PostMapping("/webhook")
    public ResponseEntity<Void> webhook(@RequestBody String payload,
                                        @RequestHeader(value = "Stripe-Signature", required = false) String signature) {
        paymentService.handleWebhook(payload, signature == null ? "" : signature);
        return ResponseEntity.ok().build();
    }
}
