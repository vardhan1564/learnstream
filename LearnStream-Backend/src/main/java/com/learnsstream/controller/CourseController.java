package com.learnsstream.controller;

import com.learnsstream.dto.CourseDtos.*;
import com.learnsstream.dto.MiscDtos.CheckoutResponse;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.CourseService;
import com.learnsstream.service.EnrollmentService;
import com.learnsstream.service.PaymentService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/courses")
public class CourseController {

    private final CourseService courseService;
    private final EnrollmentService enrollmentService;
    private final PaymentService paymentService;

    public CourseController(CourseService courseService, EnrollmentService enrollmentService, PaymentService paymentService) {
        this.courseService = courseService;
        this.enrollmentService = enrollmentService;
        this.paymentService = paymentService;
    }

    /** Public catalog. */
    @GetMapping
    public List<CourseSummary> list() {
        return courseService.listPublished(CurrentUser.getOrNull());
    }

    /** Public details. Video links are only included for enrolled students, admins and free previews. */
    @GetMapping("/{id}")
    public CourseDetail detail(@PathVariable Long id) {
        return courseService.detail(id, CurrentUser.getOrNull());
    }

    @GetMapping("/{id}/progress")
    public CourseProgress progress(@PathVariable Long id) {
        return courseService.progressFor(id, CurrentUser.get());
    }

    @PostMapping("/lessons/{lessonId}/complete")
    public CourseProgress completeLesson(@PathVariable Long lessonId) {
        return courseService.completeLesson(lessonId, CurrentUser.get());
    }

    @PostMapping("/{id}/enroll-free")
    public Map<String, Object> enrollFree(@PathVariable Long id) {
        return enrollmentService.enrollFree(id, CurrentUser.get());
    }

    @PostMapping("/{id}/claim-reward")
    public Map<String, Object> claimReward(@PathVariable Long id) {
        return enrollmentService.claimWithReward(id, CurrentUser.get());
    }

    @PostMapping("/{id}/checkout")
    public CheckoutResponse checkout(@PathVariable Long id) {
        return paymentService.createCheckout(id, CurrentUser.get());
    }
}
