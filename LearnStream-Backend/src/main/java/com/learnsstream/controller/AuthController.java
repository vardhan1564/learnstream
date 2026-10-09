package com.learnsstream.controller;

import com.learnsstream.dto.AuthDtos.*;
import com.learnsstream.security.RateLimiter;
import com.learnsstream.service.AuthService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;
    private final RateLimiter rateLimiter;
    private final String clientIpHeader;

    public AuthController(AuthService authService, RateLimiter rateLimiter,
                          @Value("${learnstream.client-ip-header:}") String clientIpHeader) {
        this.authService = authService;
        this.rateLimiter = rateLimiter;
        this.clientIpHeader = clientIpHeader.trim();
    }

    @PostMapping("/register")
    public Map<String, String> register(@Valid @RequestBody RegisterRequest req, HttpServletRequest http) {
        rateLimiter.check("register:" + ip(http), 10, 3600, "Too many sign-ups from your network. Please try again later.");
        return authService.register(req);
    }

    @PostMapping("/verify-otp")
    public Map<String, String> verify(@Valid @RequestBody VerifyOtpRequest req, HttpServletRequest http) {
        rateLimiter.check("otp:" + ip(http), 20, 600, "Too many attempts. Please wait a few minutes.");
        return authService.verifyEmail(req);
    }

    @PostMapping("/resend-otp")
    public Map<String, String> resend(@Valid @RequestBody EmailRequest req, HttpServletRequest http) {
        rateLimiter.check("resend:" + ip(http), 10, 3600, "Too many requests. Please try again later.");
        rateLimiter.check("resend-email:" + AuthService.normalizeEmail(req.email()), 3, 3600, "Too many codes requested for this email. Please try again later.");
        return authService.resendVerification(req);
    }

    @PostMapping("/login")
    public LoginResponse login(@Valid @RequestBody LoginRequest req, HttpServletRequest http) {
        rateLimiter.check("login:" + ip(http) + ":" + AuthService.normalizeEmail(req.email()), 10, 300,
                "Too many login attempts. Please wait 5 minutes and try again.");
        // Per-account limit too, so password guessing from many IPs is still capped.
        rateLimiter.check("login-email:" + AuthService.normalizeEmail(req.email()), 20, 900,
                "Too many login attempts for this account. Please wait 15 minutes and try again.");
        return authService.login(req);
    }

    @PostMapping("/forgot-password")
    public Map<String, String> forgot(@Valid @RequestBody EmailRequest req, HttpServletRequest http) {
        rateLimiter.check("forgot:" + ip(http), 5, 3600, "Too many requests. Please try again later.");
        rateLimiter.check("forgot-email:" + AuthService.normalizeEmail(req.email()), 3, 3600, "Too many reset codes requested for this email. Please try again later.");
        return authService.forgotPassword(req);
    }

    @PostMapping("/reset-password")
    public Map<String, String> reset(@Valid @RequestBody ResetPasswordRequest req, HttpServletRequest http) {
        rateLimiter.check("reset:" + ip(http), 20, 600, "Too many attempts. Please wait a few minutes.");
        return authService.resetPassword(req);
    }

    /**
     * Client IP for rate limiting. Headers like X-Forwarded-For are NOT trusted by default because anyone can fake them.
     * Behind a proxy that overwrites a known header (e.g. Cloudflare's CF-Connecting-IP on Render), set
     * learnstream.client-ip-header to that header name.
     */
    private String ip(HttpServletRequest request) {
        if (!clientIpHeader.isBlank()) {
            String value = request.getHeader(clientIpHeader);
            if (value != null && !value.isBlank()) {
                return value.trim();
            }
        }
        return request.getRemoteAddr();
    }
}
