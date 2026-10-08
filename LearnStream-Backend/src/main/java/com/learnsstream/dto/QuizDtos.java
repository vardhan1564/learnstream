package com.learnsstream.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import java.util.List;
import java.util.Map;

public final class QuizDtos {

    private QuizDtos() {}

    public record QuizSummary(
            Long id, String title, String description, String category,
            Long courseId, String courseTitle, int questionCount, int passPercentage, int maxAttempts,
            long attemptsUsed, Double bestPercentage, boolean passed, boolean published) {}

    public record Option(String key, String text) {}

    /** What a student sees - deliberately has NO correct answer field. */
    public record StudentQuestion(Long id, String questionText, List<Option> options) {}

    public record QuizForStudent(QuizSummary quiz, List<StudentQuestion> questions) {}

    public record SubmitQuizRequest(@NotNull(message = "Answers are required") Map<Long, String> answers) {}

    /** Only the score is returned - never which answers were right - so answers can't be harvested by retrying. */
    public record QuizResult(int score, int total, double percentage, boolean passed, int passPercentage,
                             long attemptsUsed, int maxAttempts) {}

    // ---------- Admin ----------

    public record QuestionRequest(
            Long id,
            @NotBlank(message = "Question text is required") @Size(max = 5000, message = "Question is too long") String questionText,
            @NotBlank(message = "Option A is required") @Size(max = 500, message = "Option A is too long") String optionA,
            @NotBlank(message = "Option B is required") @Size(max = 500, message = "Option B is too long") String optionB,
            @Size(max = 500, message = "Option C is too long") String optionC,
            @Size(max = 500, message = "Option D is too long") String optionD,
            @NotBlank(message = "Correct answer is required")
            @Pattern(regexp = "^[ABCD]$", message = "Correct answer must be A, B, C or D") String correctOption) {}

    public record QuizRequest(
            @NotBlank(message = "Title is required") @Size(max = 200, message = "Title is too long") String title,
            @Size(max = 5000, message = "Description is too long") String description,
            @Size(max = 60, message = "Category is too long") String category,
            Long courseId,
            @Min(value = 1, message = "Pass percentage must be 1-100") @Max(value = 100, message = "Pass percentage must be 1-100") Integer passPercentage,
            @Min(value = 0, message = "Max attempts cannot be negative") @Max(value = 100, message = "Max attempts is too high") Integer maxAttempts,
            Boolean published,
            @NotEmpty(message = "Add at least one question") @Size(max = 200, message = "Too many questions")
            @Valid List<QuestionRequest> questions) {}

    public record AdminQuestion(Long id, String questionText, String optionA, String optionB,
                                String optionC, String optionD, String correctOption) {}

    public record AdminQuiz(QuizSummary quiz, List<AdminQuestion> questions) {}
}
