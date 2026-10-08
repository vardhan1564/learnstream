package com.learnsstream.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import java.time.LocalDateTime;
import java.util.List;

public final class CourseDtos {

    private CourseDtos() {}

    public record CourseSummary(
            Long id, String title, String description, Double price, String thumbnail,
            String category, String level, String instructor,
            long lessonCount, long totalMinutes, boolean published, boolean enrolled) {}

    /**
     * videoUrl is null (and locked = true) unless the viewer is enrolled, an admin, or the lesson is a free preview.
     * videoType: LINK (YouTube / external URL) or UPLOAD (uploaded file; videoUrl is a short-lived signed link).
     * videoFileKey / videoFileName are only filled in for admins.
     */
    public record LessonView(
            Long id, String title, String description, String videoUrl, String videoType, Integer durationMinutes,
            int position, boolean preview, boolean locked, boolean completed, String videoFileKey, String videoFileName) {}

    public record QuizBrief(Long id, String title, int questionCount, int passPercentage, boolean passed) {}

    public record CourseProgress(
            List<Long> completedLessonIds, long completedCount, long totalCount, int percentage,
            long quizzesPassed, long quizzesTotal, boolean certificateEligible, String certificateSerial) {}

    public record CourseDetail(
            CourseSummary course, List<LessonView> lessons, List<QuizBrief> quizzes, CourseProgress progress) {}

    public record MyCourse(CourseSummary course, CourseProgress progress, String source, LocalDateTime enrolledAt) {}

    // ---------- Admin ----------

    public record LessonRequest(
            Long id,
            @NotBlank(message = "Every lesson needs a title") @Size(max = 200, message = "Lesson title is too long") String title,
            @Size(max = 5000, message = "Lesson description is too long") String description,
            @Size(max = 1000, message = "Video URL is too long")
            @Pattern(regexp = "^$|^https?://.+", message = "Video URL must start with http:// or https://") String videoUrl,
            @Pattern(regexp = "^$|^videos/[a-f0-9-]{36}\\.(mp4|webm|mov|m4v|ogv)$", message = "Invalid uploaded video reference") String videoFileKey,
            @Size(max = 255) String videoFileName,
            @Min(value = 0, message = "Duration cannot be negative") @Max(value = 1000, message = "Duration is too long") Integer durationMinutes,
            Boolean preview) {}

    public record CourseRequest(
            @NotBlank(message = "Title is required") @Size(max = 200, message = "Title is too long") String title,
            @Size(max = 10000, message = "Description is too long") String description,
            @NotNull(message = "Price is required") @PositiveOrZero(message = "Price cannot be negative")
            @Max(value = 1000000, message = "Price is too high") Double price,
            @Size(max = 1000, message = "Thumbnail URL is too long") String thumbnail,
            @Size(max = 60, message = "Category is too long") String category,
            @Size(max = 30, message = "Level is too long") String level,
            @Size(max = 100, message = "Instructor name is too long") String instructor,
            Boolean published,
            @Valid List<LessonRequest> lessons) {}

    public record AdminCourseView(CourseSummary course, List<LessonView> lessons, long enrollments) {}

    public record UploadedVideo(String key, String fileName, long size, String previewUrl) {}
}
