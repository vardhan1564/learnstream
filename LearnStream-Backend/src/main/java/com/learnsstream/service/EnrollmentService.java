package com.learnsstream.service;

import com.learnsstream.entity.Course;
import com.learnsstream.entity.Enrollment;
import com.learnsstream.entity.User;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.EnrollmentRepository;
import com.learnsstream.repository.UserRepository;
import com.learnsstream.security.AuthUser;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service
public class EnrollmentService {

    private final EnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository;
    private final CourseService courseService;
    private final RewardService rewardService;

    public EnrollmentService(EnrollmentRepository enrollmentRepository, UserRepository userRepository,
                             CourseService courseService, RewardService rewardService) {
        this.enrollmentRepository = enrollmentRepository;
        this.userRepository = userRepository;
        this.courseService = courseService;
        this.rewardService = rewardService;
    }

    /** Enroll in a course whose price is 0. */
    @Transactional
    public Map<String, Object> enrollFree(Long courseId, AuthUser viewer) {
        Course course = publishedCourse(courseId);
        if (!course.isFree()) {
            throw ApiException.badRequest("This is a paid course. Please complete the payment to enroll.");
        }
        ensureNotEnrolled(viewer.id(), courseId);
        enroll(userRepository.getReferenceById(viewer.id()), course, Enrollment.SOURCE_FREE);
        return Map.of("message", "You're enrolled in " + course.getTitle() + "!", "courseId", courseId);
    }

    /** Spend one problem-solving credit to unlock any paid course. */
    @Transactional
    public Map<String, Object> claimWithReward(Long courseId, AuthUser viewer) {
        // Lock the user row so two parallel requests can't spend the same credit twice.
        User user = userRepository.lockById(viewer.id()).orElseThrow(() -> ApiException.notFound("User"));
        Course course = publishedCourse(courseId);
        ensureNotEnrolled(user.getId(), courseId);
        if (course.isFree()) {
            enroll(user, course, Enrollment.SOURCE_FREE);
            return Map.of("message", "This course is free - you're enrolled and your credit was not used.", "courseId", courseId);
        }
        var status = rewardService.statusFor(user.getId());
        if (status.creditsAvailable() <= 0) {
            throw ApiException.forbidden("You need " + status.problemsToNextCredit()
                    + " more solved problem(s) to earn a free course.");
        }
        enroll(user, course, Enrollment.SOURCE_REWARD);
        return Map.of("message", "Reward claimed! " + course.getTitle() + " is now unlocked.", "courseId", courseId);
    }

    /** Admin: give a student access manually (e.g. offline payment, scholarship). */
    @Transactional
    public void grantByAdmin(Long userId, Long courseId) {
        User user = userRepository.findById(userId).orElseThrow(() -> ApiException.notFound("User"));
        Course course = courseService.requireCourse(courseId);
        ensureNotEnrolled(userId, courseId);
        enroll(user, course, Enrollment.SOURCE_ADMIN);
    }

    /** Idempotent: does nothing if already enrolled. */
    @Transactional
    public void enroll(User user, Course course, String source) {
        if (enrollmentRepository.existsByUserIdAndCourseId(user.getId(), course.getId())) {
            return;
        }
        Enrollment e = new Enrollment();
        e.setUser(user);
        e.setCourse(course);
        e.setSource(source);
        enrollmentRepository.save(e);
    }

    private Course publishedCourse(Long courseId) {
        Course course = courseService.requireCourse(courseId);
        if (!course.isPublished()) {
            throw ApiException.notFound("Course");
        }
        return course;
    }

    private void ensureNotEnrolled(Long userId, Long courseId) {
        if (enrollmentRepository.existsByUserIdAndCourseId(userId, courseId)) {
            throw ApiException.conflict("You're already enrolled in this course");
        }
    }
}
