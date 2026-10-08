package com.learnsstream.controller;

import com.learnsstream.dto.AuthDtos.*;
import com.learnsstream.security.RateLimiter;
import com.learnsstream.service.AuthService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;
    private final RateLimiter rateLimiter;

    public AuthController(AuthService authService, RateLimiter rateLimiter) {
        this.authService = authService;
        this.rateLimiter = rateLimiter;
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
        return authService.resendVerification(req);
    }

    @PostMapping("/login")
    public LoginResponse login(@Valid @RequestBody LoginRequest req, HttpServletRequest http) {
        rateLimiter.check("login:" + ip(http) + ":" + AuthService.normalizeEmail(req.email()), 10, 300,
                "Too many login attempts. Please wait 5 minutes and try again.");
        return authService.login(req);
    }

    @PostMapping("/forgot-password")
    public Map<String, String> forgot(@Valid @RequestBody EmailRequest req, HttpServletRequest http) {
        rateLimiter.check("forgot:" + ip(http), 5, 3600, "Too many requests. Please try again later.");
        return authService.forgotPassword(req);
    }

    @PostMapping("/reset-password")
    public Map<String, String> reset(@Valid @RequestBody ResetPasswordRequest req, HttpServletRequest http) {
        rateLimiter.check("reset:" + ip(http), 20, 600, "Too many attempts. Please wait a few minutes.");
        return authService.resetPassword(req);
    }

    /**
     * Client IP for rate limiting. X-Forwarded-For is NOT read here because anyone can fake it;
     * behind a trusted proxy set server.forward-headers-strategy=native and Tomcat fills getRemoteAddr() correctly.
     */
    static String ip(HttpServletRequest request) {
        return request.getRemoteAddr();
    }
}
