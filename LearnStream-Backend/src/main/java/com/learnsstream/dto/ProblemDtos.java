package com.learnsstream.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

public final class ProblemDtos {

    private ProblemDtos() {}

    public record ProblemSummary(Long id, String title, String difficulty, String tags, boolean published, boolean solved) {}

    public record SampleTest(String input, String expectedOutput) {}

    /** Student view: only sample tests are included; hidden tests are just counted. */
    public record ProblemDetail(
            Long id, String title, String description, String difficulty,
            String inputFormat, String outputFormat, String constraintsText, String tags,
            Map<String, String> starterCode, List<SampleTest> samples, int hiddenTestCount, boolean solved) {}

    public record RunRequest(
            @NotBlank(message = "Language is required") String language,
            @NotBlank(message = "Code cannot be empty") @Size(max = 65536, message = "Code is too long (max 64 KB)") String code,
            @Size(max = 10000, message = "Custom input is too long") String customInput) {}

    /** input / expected / actual are null for hidden test cases. */
    public record TestResult(int index, boolean hidden, boolean passed, String status,
                             String input, String expectedOutput, String actualOutput, String time, Integer memory) {}

    public record RunResponse(
            String status, int passedCount, int totalCount,
            String compileOutput, String stderr, List<TestResult> results,
            boolean solved, boolean firstSolve, RewardDtos.RewardStatus rewards) {}

    public record SubmissionView(Long id, String language, String status, int passedCount, int totalCount,
                                 LocalDateTime submittedAt, String code) {}

    public record LanguageInfo(String id, String name) {}

    // ---------- Admin ----------

    public record TestCaseRequest(
            @Size(max = 20000, message = "Test input is too long") String input,
            @NotNull(message = "Every test case needs an expected output")
            @Size(max = 20000, message = "Expected output is too long") String expectedOutput,
            Boolean sample) {}

    public record ProblemRequest(
            @NotBlank(message = "Title is required") @Size(max = 200, message = "Title is too long") String title,
            @NotBlank(message = "Description is required") @Size(max = 20000, message = "Description is too long") String description,
            @NotBlank(message = "Difficulty is required")
            @Pattern(regexp = "^(EASY|MEDIUM|HARD)$", message = "Difficulty must be EASY, MEDIUM or HARD") String difficulty,
            @Size(max = 5000) String inputFormat,
            @Size(max = 5000) String outputFormat,
            @Size(max = 5000) String constraintsText,
            @Size(max = 255, message = "Tags are too long") String tags,
            @Size(max = 20000) String starterJava,
            @Size(max = 20000) String starterPython,
            @Size(max = 20000) String starterCpp,
            @Size(max = 20000) String starterJavascript,
            Boolean published,
            @NotEmpty(message = "Add at least one test case") @Size(max = 30, message = "Maximum 30 test cases")
            @Valid List<TestCaseRequest> testCases) {}

    public record AdminTestCase(Long id, String input, String expectedOutput, boolean sample) {}

    public record AdminProblem(
            Long id, String title, String description, String difficulty,
            String inputFormat, String outputFormat, String constraintsText, String tags,
            String starterJava, String starterPython, String starterCpp, String starterJavascript,
            boolean published, List<AdminTestCase> testCases, LocalDateTime createdAt) {}
}
