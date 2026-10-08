package com.learnsstream.controller;

import com.learnsstream.dto.CourseDtos.AdminCourseView;
import com.learnsstream.dto.CourseDtos.CourseRequest;
import com.learnsstream.dto.CourseDtos.UploadedVideo;
import com.learnsstream.dto.MiscDtos.*;
import com.learnsstream.dto.ProblemDtos.AdminProblem;
import com.learnsstream.dto.ProblemDtos.ProblemRequest;
import com.learnsstream.dto.QuizDtos.AdminQuiz;
import com.learnsstream.dto.QuizDtos.QuizRequest;
import com.learnsstream.dto.QuizDtos.QuizSummary;
import com.learnsstream.dto.UserDtos.AdminUserView;
import com.learnsstream.dto.UserDtos.RoleUpdateRequest;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.*;
import jakarta.validation.Valid;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

/** Everything here requires ROLE_ADMIN (checked in SecurityConfig AND here). */
@RestController
@RequestMapping("/api/admin")
@PreAuthorize("hasAuthority('ROLE_ADMIN')")
public class AdminController {

    private final AdminService adminService;
    private final CourseService courseService;
    private final QuizService quizService;
    private final ProblemService problemService;
    private final RoadmapService roadmapService;
    private final LeaderboardService leaderboardService;
    private final PaymentService paymentService;
    private final EnrollmentService enrollmentService;
    private final VideoStorageService videoStorage;

    public AdminController(AdminService adminService, CourseService courseService, QuizService quizService,
                           ProblemService problemService, RoadmapService roadmapService,
                           LeaderboardService leaderboardService, PaymentService paymentService,
                           EnrollmentService enrollmentService, VideoStorageService videoStorage) {
        this.adminService = adminService;
        this.courseService = courseService;
        this.quizService = quizService;
        this.problemService = problemService;
        this.roadmapService = roadmapService;
        this.leaderboardService = leaderboardService;
        this.paymentService = paymentService;
        this.enrollmentService = enrollmentService;
        this.videoStorage = videoStorage;
    }

    // ---------- Video upload ----------
    /** Upload a lesson video (stored on disk or in R2/S3 - never in the database). Returns the key to put on the lesson. */
    @PostMapping(value = "/videos", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public UploadedVideo uploadVideo(@RequestParam("file") MultipartFile file) {
        VideoStorageService.StoredVideo stored = videoStorage.store(file);
        return new UploadedVideo(stored.key(), stored.originalName(), stored.size(), videoStorage.playbackUrl(stored.key()));
    }

    // ---------- Dashboard ----------
    @GetMapping("/stats")
    public Map<String, Object> stats() {
        return adminService.stats();
    }

    @GetMapping("/leaderboard")
    public List<LeaderboardEntry> leaderboard(@RequestParam(defaultValue = "100") int limit) {
        return leaderboardService.leaderboard(limit, CurrentUser.get(), true);
    }

    @GetMapping("/payments")
    public List<PaymentView> payments(@RequestParam(defaultValue = "50") int limit) {
        return paymentService.recentPayments(limit);
    }

    // ---------- Courses ----------
    @GetMapping("/courses")
    public List<AdminCourseView> courses() {
        return courseService.adminList();
    }

    @GetMapping("/courses/{id}")
    public AdminCourseView course(@PathVariable Long id) {
        return courseService.adminGet(id);
    }

    @PostMapping("/courses")
    public AdminCourseView createCourse(@Valid @RequestBody CourseRequest req) {
        return courseService.create(req);
    }

    @PutMapping("/courses/{id}")
    public AdminCourseView updateCourse(@PathVariable Long id, @Valid @RequestBody CourseRequest req) {
        return courseService.update(id, req);
    }

    @DeleteMapping("/courses/{id}")
    public Map<String, String> deleteCourse(@PathVariable Long id) {
        courseService.delete(id);
        return Map.of("message", "Course deleted");
    }

    // ---------- Quizzes / MCQs ----------
    @GetMapping("/quizzes")
    public List<QuizSummary> quizzes() {
        return quizService.adminList();
    }

    @GetMapping("/quizzes/{id}")
    public AdminQuiz quiz(@PathVariable Long id) {
        return quizService.adminGet(id);
    }

    @PostMapping("/quizzes")
    public AdminQuiz createQuiz(@Valid @RequestBody QuizRequest req) {
        return quizService.create(req);
    }

    @PutMapping("/quizzes/{id}")
    public AdminQuiz updateQuiz(@PathVariable Long id, @Valid @RequestBody QuizRequest req) {
        return quizService.update(id, req);
    }

    @DeleteMapping("/quizzes/{id}")
    public Map<String, String> deleteQuiz(@PathVariable Long id) {
        quizService.delete(id);
        return Map.of("message", "Quiz deleted");
    }

    // ---------- Coding problems ----------
    @GetMapping("/problems")
    public List<AdminProblem> problems() {
        return problemService.adminList();
    }

    @GetMapping("/problems/{id}")
    public AdminProblem problem(@PathVariable Long id) {
        return problemService.adminGet(id);
    }

    @PostMapping("/problems")
    public AdminProblem createProblem(@Valid @RequestBody ProblemRequest req) {
        return problemService.create(req);
    }

    @PutMapping("/problems/{id}")
    public AdminProblem updateProblem(@PathVariable Long id, @Valid @RequestBody ProblemRequest req) {
        return problemService.update(id, req);
    }

    @DeleteMapping("/problems/{id}")
    public Map<String, String> deleteProblem(@PathVariable Long id) {
        problemService.delete(id);
        return Map.of("message", "Problem deleted");
    }

    // ---------- Roadmaps ----------
    @GetMapping("/roadmaps")
    public List<RoadmapDetail> roadmaps() {
        return roadmapService.adminList();
    }

    @PostMapping("/roadmaps")
    public RoadmapDetail createRoadmap(@Valid @RequestBody RoadmapRequest req) {
        return roadmapService.create(req);
    }

    @PutMapping("/roadmaps/{id}")
    public RoadmapDetail updateRoadmap(@PathVariable Long id, @Valid @RequestBody RoadmapRequest req) {
        return roadmapService.update(id, req);
    }

    @DeleteMapping("/roadmaps/{id}")
    public Map<String, String> deleteRoadmap(@PathVariable Long id) {
        roadmapService.delete(id);
        return Map.of("message", "Roadmap deleted");
    }

    // ---------- Users ----------
    @GetMapping("/users")
    public List<AdminUserView> users(@RequestParam(required = false) String query) {
        return adminService.users(query);
    }

    @PutMapping("/users/{id}/role")
    public Map<String, String> updateRole(@PathVariable Long id, @Valid @RequestBody RoleUpdateRequest req) {
        adminService.updateRole(id, req.role(), CurrentUser.get());
        return Map.of("message", "Role updated");
    }

    @PostMapping("/users/{userId}/enroll/{courseId}")
    public Map<String, String> grantCourse(@PathVariable Long userId, @PathVariable Long courseId) {
        enrollmentService.grantByAdmin(userId, courseId);
        return Map.of("message", "Course access granted");
    }
}
