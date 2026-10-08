package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * A LeetCode / HackerRank style problem. Programs read from standard input and
 * print to standard output; each test case is (input, expected output).
 */
@Entity
@Table(name = "problems")
@Getter @Setter @NoArgsConstructor
public class Problem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false, columnDefinition = "MEDIUMTEXT")
    private String description;

    /** EASY, MEDIUM, HARD */
    @Column(nullable = false, length = 10)
    private String difficulty = "EASY";

    @Column(columnDefinition = "MEDIUMTEXT")
    private String inputFormat;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String outputFormat;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String constraintsText;

    /** Comma separated, e.g. "Arrays,Hashing" */
    @Column(length = 255)
    private String tags;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String starterJava;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String starterPython;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String starterCpp;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String starterJavascript;

    @Column(nullable = false)
    private boolean published = true;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @OneToMany(mappedBy = "problem", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("position ASC")
    private List<TestCase> testCases = new ArrayList<>();
}
