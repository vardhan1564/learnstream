package com.learnsstream.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;
import java.util.List;

/** Certificates, payments, leaderboard and roadmaps. */
public final class MiscDtos {

    private MiscDtos() {}

    // ---------- Certificates ----------
    public record CertificateView(String serialNumber, Long courseId, String courseTitle, LocalDateTime issuedAt) {}

    public record CertificateVerification(boolean valid, String serialNumber, String studentName,
                                          String courseTitle, LocalDateTime issuedAt) {}

    // ---------- Payments ----------
    public record CheckoutResponse(String url) {}

    public record VerifyPaymentRequest(@NotBlank(message = "Session id is required") String sessionId) {}

    public record VerifyPaymentResponse(Long courseId, String courseTitle, boolean enrolled) {}

    public record PaymentView(Long id, String studentName, String studentEmail, String courseTitle,
                              double amount, String currency, LocalDateTime paidAt) {}

    // ---------- Leaderboard ----------
    public record LeaderboardEntry(int rank, Long userId, String fullName, String email,
                                   long problemsSolved, long hardSolved, long quizPoints, long points, boolean me) {}

    // ---------- Roadmaps ----------
    public record RoadmapSummary(Long id, String title, String description, String level, String duration,
                                 int stepCount, int completedCount, boolean published) {}

    public record RoadmapStepView(Long id, String title, String description, String resourceUrl,
                                  Long courseId, String courseTitle, int position, boolean completed) {}

    public record RoadmapDetail(RoadmapSummary roadmap, List<RoadmapStepView> steps) {}

    public record RoadmapStepRequest(
            Long id,
            @NotBlank(message = "Every step needs a title") @Size(max = 200, message = "Step title is too long") String title,
            @Size(max = 5000, message = "Step description is too long") String description,
            @Size(max = 1000, message = "Resource URL is too long")
            @Pattern(regexp = "^$|^https?://.+", message = "Resource URL must start with http:// or https://") String resourceUrl,
            Long courseId) {}

    public record RoadmapRequest(
            @NotBlank(message = "Title is required") @Size(max = 200, message = "Title is too long") String title,
            @Size(max = 5000, message = "Description is too long") String description,
            @Size(max = 30) String level,
            @Size(max = 50) String duration,
            Boolean published,
            @NotEmpty(message = "Add at least one step") @Size(max = 100, message = "Too many steps")
            @Valid List<RoadmapStepRequest> steps) {}
}
