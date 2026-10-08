package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Getter @Setter @NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false, length = 150)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false, length = 100)
    private String fullName;

    @Column(nullable = false, length = 20)
    private String role = Role.STUDENT;

    @Column(nullable = false)
    private boolean verified = false;

    /** BCrypt hash of the current one-time password (never stored in plain text). */
    private String otpHash;

    /** VERIFY_EMAIL or RESET_PASSWORD */
    @Column(length = 20)
    private String otpPurpose;

    private LocalDateTime otpExpiresAt;

    private LocalDateTime otpSentAt;

    @Column(nullable = false)
    private int otpAttempts = 0;

    /** Tokens issued before this moment are rejected (logs out other devices after a password change). */
    private LocalDateTime passwordChangedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    public boolean isAdmin() {
        return Role.ADMIN.equals(role);
    }
}
