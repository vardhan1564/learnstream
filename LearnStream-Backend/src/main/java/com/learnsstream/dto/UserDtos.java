package com.learnsstream.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;
import java.util.List;

public final class UserDtos {

    private UserDtos() {}

    public record UpdateProfileRequest(
            @NotBlank(message = "Full name is required")
            @Size(min = 2, max = 100, message = "Full name must be 2-100 characters") String fullName) {}

    public record ChangePasswordRequest(
            @NotBlank(message = "Current password is required") String currentPassword,
            @NotBlank(message = "New password is required")
            @Pattern(regexp = AuthDtos.PASSWORD_RULE, message = AuthDtos.PASSWORD_MESSAGE) String newPassword) {}

    public record ProfileResponse(
            Long id, String fullName, String email, String role, LocalDateTime memberSince,
            long coursesEnrolled, long coursesCompleted, long certificates,
            long problemsSolved, long quizzesPassed, long points,
            RewardDtos.RewardStatus rewards) {}

    public record AdminUserView(
            Long id, String fullName, String email, String role, boolean verified,
            LocalDateTime createdAt, List<String> enrolledCourses, long problemsSolved) {}

    public record RoleUpdateRequest(
            @NotBlank(message = "Role is required")
            @Pattern(regexp = "^(ROLE_STUDENT|ROLE_ADMIN)$", message = "Role must be ROLE_STUDENT or ROLE_ADMIN") String role) {}
}
