package com.learnsstream.service;

import com.learnsstream.dto.UserDtos.AdminUserView;
import com.learnsstream.entity.Role;
import com.learnsstream.entity.Submission;
import com.learnsstream.entity.User;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.*;
import com.learnsstream.security.AuthUser;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class AdminService {

    private final UserRepository userRepository;
    private final CourseRepository courseRepository;
    private final ProblemRepository problemRepository;
    private final QuizRepository quizRepository;
    private final RoadmapRepository roadmapRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final CertificateRepository certificateRepository;
    private final SubmissionRepository submissionRepository;
    private final PaymentRepository paymentRepository;

    public AdminService(UserRepository userRepository, CourseRepository courseRepository,
                        ProblemRepository problemRepository, QuizRepository quizRepository,
                        RoadmapRepository roadmapRepository, EnrollmentRepository enrollmentRepository,
                        CertificateRepository certificateRepository, SubmissionRepository submissionRepository,
                        PaymentRepository paymentRepository) {
        this.userRepository = userRepository;
        this.courseRepository = courseRepository;
        this.problemRepository = problemRepository;
        this.quizRepository = quizRepository;
        this.roadmapRepository = roadmapRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.certificateRepository = certificateRepository;
        this.submissionRepository = submissionRepository;
        this.paymentRepository = paymentRepository;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> stats() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("totalStudents", userRepository.countByRole(Role.STUDENT));
        m.put("totalAdmins", userRepository.countByRole(Role.ADMIN));
        m.put("totalCourses", courseRepository.count());
        m.put("totalProblems", problemRepository.count());
        m.put("totalQuizzes", quizRepository.count());
        m.put("totalRoadmaps", roadmapRepository.count());
        m.put("totalEnrollments", enrollmentRepository.count());
        m.put("certificatesIssued", certificateRepository.count());
        m.put("acceptedSubmissions", submissionRepository.countByStatus(Submission.ACCEPTED));
        m.put("revenue", paymentRepository.sumPaidAmount() / 100.0);
        return m;
    }

    /** Small public numbers for the home page. */
    @Transactional(readOnly = true)
    public Map<String, Long> publicStats() {
        return Map.of(
                "courses", (long) courseRepository.findByPublishedTrueOrderByCreatedAtDesc().size(),
                "problems", (long) problemRepository.findByPublishedTrueOrderByIdAsc().size(),
                "students", userRepository.countByRole(Role.STUDENT),
                "quizzes", (long) quizRepository.findByPublishedTrueOrderByCreatedAtDesc().size());
    }

    @Transactional(readOnly = true)
    public List<AdminUserView> users(String query) {
        PageRequest page = PageRequest.of(0, 100);
        List<User> users = (query == null || query.isBlank())
                ? userRepository.findRecent(page)
                : userRepository.search(query.trim(), page);
        return users.stream()
                .map(u -> new AdminUserView(u.getId(), u.getFullName(), u.getEmail(), u.getRole(), u.isVerified(),
                        u.getCreatedAt(), enrollmentRepository.findCourseTitlesByUserId(u.getId()),
                        submissionRepository.countSolvedProblems(u.getId())))
                .toList();
    }

    @Transactional
    public void updateRole(Long userId, String role, AuthUser actingAdmin) {
        if (!Role.isValid(role)) {
            throw ApiException.badRequest("Invalid role");
        }
        User user = userRepository.findById(userId).orElseThrow(() -> ApiException.notFound("User"));
        if (user.getId().equals(actingAdmin.id()) && !Role.ADMIN.equals(role)) {
            throw ApiException.badRequest("You can't remove your own admin access");
        }
        if (user.isAdmin() && !Role.ADMIN.equals(role) && userRepository.countByRole(Role.ADMIN) <= 1) {
            throw ApiException.badRequest("There must be at least one admin");
        }
        if (Role.ADMIN.equals(role) && !user.isVerified()) {
            throw ApiException.badRequest("Only verified users can become admins");
        }
        user.setRole(role);
        userRepository.save(user);
    }
}
