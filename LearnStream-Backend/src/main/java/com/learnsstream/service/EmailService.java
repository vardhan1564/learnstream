package com.learnsstream.service;

import com.learnsstream.exception.EmailSendException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

@Service
public class EmailService {

    private static final Logger log = LoggerFactory.getLogger(EmailService.class);
    private static final String BREVO_URL = "https://api.brevo.com/v3/smtp/email";

    private final JavaMailSender mailSender;
    private final HttpClient httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();

    @Value("${spring.mail.username:}")
    private String fromEmail;

    @Value("${learnstream.mail.enabled:true}")
    private boolean mailEnabled;

    // When set, emails go through Brevo's HTTPS API instead of SMTP.
    // Needed on hosts that block outbound SMTP ports (e.g. Render's free tier).
    @Value("${learnstream.mail.brevo-api-key:}")
    private String brevoApiKey;

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
            if (brevoApiKey != null && !brevoApiKey.isBlank()) {
                sendViaBrevo(to, subject, text);
                return;
            }
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

    private void sendViaBrevo(String to, String subject, String text) throws Exception {
        String body = "{\"sender\":{\"name\":\"LearnStream\",\"email\":" + json(fromEmail) + "},"
                + "\"to\":[{\"email\":" + json(to) + "}],"
                + "\"subject\":" + json(subject) + ","
                + "\"textContent\":" + json(text) + "}";
        HttpRequest request = HttpRequest.newBuilder(URI.create(BREVO_URL))
                .timeout(Duration.ofSeconds(15))
                .header("api-key", brevoApiKey)
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() / 100 != 2) {
            throw new IllegalStateException("Brevo returned " + response.statusCode() + ": " + response.body());
        }
    }

    private static String json(String value) {
        StringBuilder sb = new StringBuilder("\"");
        for (char c : value.toCharArray()) {
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
                }
            }
        }
        return sb.append('"').toString();
    }
}
