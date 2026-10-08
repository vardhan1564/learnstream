package com.learnsstream.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public final class AuthDtos {

    private AuthDtos() {}

    public static final String PASSWORD_RULE = "^(?=.*[A-Za-z])(?=.*\\d).{8,72}$";
    public static final String PASSWORD_MESSAGE = "Password must be 8-72 characters and contain at least one letter and one number";

    public record RegisterRequest(
            @NotBlank(message = "Full name is required")
            @Size(min = 2, max = 100, message = "Full name must be 2-100 characters")
            String fullName,
            @NotBlank(message = "Email is required") @Email(message = "Enter a valid email")
            @Size(max = 150, message = "Email is too long")
            String email,
            @NotBlank(message = "Password is required") @Pattern(regexp = PASSWORD_RULE, message = PASSWORD_MESSAGE)
            String password) {}

    public record VerifyOtpRequest(
            @NotBlank(message = "Email is required") @Email(message = "Enter a valid email") String email,
            @NotBlank(message = "OTP is required") @Pattern(regexp = "^\\d{6}$", message = "OTP must be 6 digits") String otp) {}

    public record EmailRequest(
            @NotBlank(message = "Email is required") @Email(message = "Enter a valid email") String email) {}

    public record LoginRequest(
            @NotBlank(message = "Email is required") @Email(message = "Enter a valid email") String email,
            @NotBlank(message = "Password is required") String password) {}

    public record ResetPasswordRequest(
            @NotBlank(message = "Email is required") @Email(message = "Enter a valid email") String email,
            @NotBlank(message = "OTP is required") @Pattern(regexp = "^\\d{6}$", message = "OTP must be 6 digits") String otp,
            @NotBlank(message = "New password is required") @Pattern(regexp = PASSWORD_RULE, message = PASSWORD_MESSAGE) String newPassword) {}

    public record UserInfo(Long id, String fullName, String email, String role) {}

    public record LoginResponse(String token, UserInfo user) {}
}
