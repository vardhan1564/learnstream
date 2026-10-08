package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "submissions", indexes = {
        @Index(name = "idx_submission_user_problem", columnList = "user_id,problem_id"),
        @Index(name = "idx_submission_status", columnList = "status")
})
@Getter @Setter @NoArgsConstructor
public class Submission {

    public static final String ACCEPTED = "ACCEPTED";

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "problem_id", nullable = false)
    private Problem problem;

    @Column(nullable = false, length = 20)
    private String language;

    @Column(nullable = false, columnDefinition = "MEDIUMTEXT")
    private String code;

    /** ACCEPTED, WRONG_ANSWER, COMPILATION_ERROR, RUNTIME_ERROR, TIME_LIMIT_EXCEEDED, ERROR */
    @Column(nullable = false, length = 40)
    private String status;

    private int passedCount;

    private int totalCount;

    @Column(nullable = false)
    private LocalDateTime submittedAt = LocalDateTime.now();
}
