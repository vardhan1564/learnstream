package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** Sample test cases are shown to students; hidden ones never leave the server. */
@Entity
@Table(name = "problem_test_cases")
@Getter @Setter @NoArgsConstructor
public class TestCase {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "problem_id", nullable = false)
    private Problem problem;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String input;

    @Column(nullable = false, columnDefinition = "MEDIUMTEXT")
    private String expectedOutput;

    @Column(nullable = false)
    private boolean sample = false;

    @Column(nullable = false)
    private int position = 0;
}
