package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "enrollments", uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "course_id"}))
@Getter @Setter @NoArgsConstructor
public class Enrollment {

    public static final String SOURCE_PAID = "PAID";
    public static final String SOURCE_FREE = "FREE";
    public static final String SOURCE_REWARD = "REWARD";
    public static final String SOURCE_ADMIN = "ADMIN";

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "course_id", nullable = false)
    private Course course;

    /** PAID, FREE, REWARD (claimed with problem-solving credits) or ADMIN (granted manually) */
    @Column(nullable = false, length = 20)
    private String source;

    @Column(nullable = false)
    private LocalDateTime enrolledAt = LocalDateTime.now();
}
