package com.learnsstream.service;

import com.learnsstream.exception.EmailSendException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    private static final Logger log = LoggerFactory.getLogger(EmailService.class);

    private final JavaMailSender mailSender;

    @Value("${spring.mail.username:}")
    private String fromEmail;

    @Value("${learnstream.mail.enabled:true}")
    private boolean mailEnabled;

    public EmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    public void sendOtp(String to, String otp, String purpose) {
        boolean reset = "RESET_PASSWORD".equals(purpose);
        String subject = reset ? "Reset your LearnStream password" : "Verify your LearnStream account";
        String text = (reset
                ? "Use this code to reset your LearnStream password:\n\n"
                : "Welcome to LearnStream! Use this code to verify your email:\n\n")
                + "    " + otp + "\n\n"
                + "The code expires in 10 minutes. If you didn't request it, you can ignore this email.\n\n"
                + "- Team LearnStream";

        if (!mailEnabled) {
            // Local development without SMTP (learnstream.mail.enabled=false): print the code to test sign-up.
            log.warn("MAIL DISABLED - OTP for {} ({}): {}", to, purpose, otp);
            return;
        }
        if (fromEmail == null || fromEmail.isBlank()) {
            log.error("spring.mail.username is not set - cannot send OTP emails. Set it, or set learnstream.mail.enabled=false for local testing.");
            throw new EmailSendException("Email is not configured on the server. Please contact the admin.");
        }
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromEmail);
            message.setTo(to);
            message.setSubject(subject);
            message.setText(text);
            mailSender.send(message);
        } catch (Exception e) {
            log.error("Failed to send OTP email to {}: {}", to, e.getMessage());
            throw new EmailSendException("We couldn't send the verification email right now. Please try again in a minute.");
        }
    }
}
