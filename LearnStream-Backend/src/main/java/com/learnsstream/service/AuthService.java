package com.learnsstream.service;

import com.learnsstream.dto.AuthDtos.*;
import com.learnsstream.entity.Role;
import com.learnsstream.entity.User;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.UserRepository;
import com.learnsstream.security.JwtUtils;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Locale;
import java.util.Map;

@Service
public class AuthService {

    public static final String PURPOSE_VERIFY = "VERIFY_EMAIL";
    public static final String PURPOSE_RESET = "RESET_PASSWORD";

    private static final int OTP_VALID_MINUTES = 10;
    private static final int OTP_RESEND_COOLDOWN_SECONDS = 60;
    private static final int OTP_MAX_ATTEMPTS = 5;

    private final SecureRandom random = new SecureRandom();
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;

    public AuthService(UserRepository userRepository, EmailService emailService,
                       PasswordEncoder passwordEncoder, JwtUtils jwtUtils) {
        this.userRepository = userRepository;
        this.emailService = emailService;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtils = jwtUtils;
    }

    public static String normalizeEmail(String email) {
        return email == null ? "" : email.trim().toLowerCase(Locale.ROOT);
    }

    /** Every new account is a STUDENT. Admins are created on startup or promoted by another admin. */
    @Transactional
    public Map<String, String> register(RegisterRequest req) {
        String email = normalizeEmail(req.email());
        User user = userRepository.findByEmailIgnoreCase(email).orElse(null);

        if (user != null && user.isVerified()) {
            throw ApiException.conflict("An account with this email already exists. Please log in.");
        }
        if (user == null) {
            user = new User();
            user.setEmail(email);
            user.setRole(Role.STUDENT);
        }
        // Unverified account re-registering: just update details and send a fresh code.
        user.setFullName(req.fullName().trim());
        user.setPassword(passwordEncoder.encode(req.password()));
        user.setVerified(false);
        issueOtp(user, PURPOSE_VERIFY, true);
        return Map.of("message", "Account created. We've sent a 6-digit code to " + email + ".", "email", email);
    }

    @Transactional(noRollbackFor = ApiException.class)
    public Map<String, String> verifyEmail(VerifyOtpRequest req) {
        User user = userRepository.findByEmailIgnoreCase(normalizeEmail(req.email()))
                .orElseThrow(() -> ApiException.badRequest("Invalid or expired code"));
        if (user.isVerified()) {
            return Map.of("message", "Your email is already verified. Please log in.");
        }
        checkOtp(user, req.otp(), PURPOSE_VERIFY);
        user.setVerified(true);
        clearOtp(user);
        userRepository.save(user);
        return Map.of("message", "Email verified! You can now log in.");
    }

    @Transactional
    public Map<String, String> resendVerification(EmailRequest req) {
        userRepository.findByEmailIgnoreCase(normalizeEmail(req.email()))
                .filter(u -> !u.isVerified())
                .ifPresent(u -> issueOtp(u, PURPOSE_VERIFY, true));
        // Same answer whether or not the account exists (prevents email enumeration).
        return Map.of("message", "If that account is waiting for verification, a new code has been sent.");
    }

    // noRollbackFor: the fresh OTP sent to an unverified user must be saved even though we return an error.
    @Transactional(noRollbackFor = ApiException.class)
    public LoginResponse login(LoginRequest req) {
        User user = userRepository.findByEmailIgnoreCase(normalizeEmail(req.email())).orElse(null);
        if (user == null || !passwordEncoder.matches(req.password(), user.getPassword())) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "Invalid email or password");
        }
        if (!user.isVerified()) {
            issueOtp(user, PURPOSE_VERIFY, false); // send a fresh code unless one was sent a moment ago
            throw new ApiException(HttpStatus.FORBIDDEN,
                    "Please verify your email first. We've sent a code to " + user.getEmail() + ".",
                    "EMAIL_NOT_VERIFIED");
        }
        String token = jwtUtils.generateToken(user.getId(), user.getEmail(), user.getRole());
        return new LoginResponse(token, toInfo(user));
    }

    @Transactional
    public Map<String, String> forgotPassword(EmailRequest req) {
        userRepository.findByEmailIgnoreCase(normalizeEmail(req.email()))
                .filter(User::isVerified)
                .ifPresent(u -> issueOtp(u, PURPOSE_RESET, false));
        return Map.of("message", "If an account exists for that email, a reset code has been sent.");
    }

    @Transactional(noRollbackFor = ApiException.class)
    public Map<String, String> resetPassword(ResetPasswordRequest req) {
        User user = userRepository.findByEmailIgnoreCase(normalizeEmail(req.email()))
                .orElseThrow(() -> ApiException.badRequest("Invalid or expired code"));
        checkOtp(user, req.otp(), PURPOSE_RESET);
        user.setPassword(passwordEncoder.encode(req.newPassword()));
        user.setPasswordChangedAt(LocalDateTime.now().truncatedTo(java.time.temporal.ChronoUnit.SECONDS));
        clearOtp(user);
        userRepository.save(user);
        return Map.of("message", "Password updated. You can now log in with your new password.");
    }

    public static UserInfo toInfo(User user) {
        return new UserInfo(user.getId(), user.getFullName(), user.getEmail(), user.getRole());
    }

    // ------------------------------------------------------------------

    /**
     * Generates, stores (hashed) and emails a new 6-digit code.
     * @param strictCooldown true = tell the user to wait; false = silently skip if a code was just sent
     */
    private void issueOtp(User user, String purpose, boolean strictCooldown) {
        LocalDateTime now = LocalDateTime.now();
        if (user.getOtpSentAt() != null && purpose.equals(user.getOtpPurpose())) {
            long secondsSince = Duration.between(user.getOtpSentAt(), now).getSeconds();
            if (secondsSince < OTP_RESEND_COOLDOWN_SECONDS) {
                if (strictCooldown) {
                    throw ApiException.tooManyRequests("Please wait " + (OTP_RESEND_COOLDOWN_SECONDS - secondsSince)
                            + " seconds before requesting another code.");
                }
                return; // a valid code was sent moments ago
            }
        }
        String otp = String.format("%06d", random.nextInt(1_000_000));
        user.setOtpHash(passwordEncoder.encode(otp));
        user.setOtpPurpose(purpose);
        user.setOtpExpiresAt(now.plusMinutes(OTP_VALID_MINUTES));
        user.setOtpSentAt(now);
        user.setOtpAttempts(0);
        userRepository.save(user);
        emailService.sendOtp(user.getEmail(), otp, purpose); // throws -> transaction rolls back
    }

    private void checkOtp(User user, String otp, String purpose) {
        if (user.getOtpHash() == null || !purpose.equals(user.getOtpPurpose())
                || user.getOtpExpiresAt() == null || user.getOtpExpiresAt().isBefore(LocalDateTime.now())) {
            throw ApiException.badRequest("This code has expired. Please request a new one.");
        }
        if (user.getOtpAttempts() >= OTP_MAX_ATTEMPTS) {
            throw ApiException.tooManyRequests("Too many wrong attempts. Please request a new code.");
        }
        if (!passwordEncoder.matches(otp, user.getOtpHash())) {
            user.setOtpAttempts(user.getOtpAttempts() + 1);
            userRepository.save(user);
            int left = OTP_MAX_ATTEMPTS - user.getOtpAttempts();
            throw ApiException.badRequest(left > 0
                    ? "Incorrect code. " + left + " attempt" + (left == 1 ? "" : "s") + " left."
                    : "Too many wrong attempts. Please request a new code.");
        }
    }

    private void clearOtp(User user) {
        user.setOtpHash(null);
        user.setOtpPurpose(null);
        user.setOtpExpiresAt(null);
        user.setOtpAttempts(0);
    }
}
