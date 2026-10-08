package com.learnsstream.service;

import com.learnsstream.dto.AuthDtos.LoginResponse;
import com.learnsstream.dto.AuthDtos.UserInfo;
import com.learnsstream.dto.UserDtos.*;
import com.learnsstream.entity.User;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.*;
import com.learnsstream.security.JwtUtils;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final CertificateRepository certificateRepository;
    private final QuizAttemptRepository quizAttemptRepository;
    private final RewardService rewardService;
    private final CourseService courseService;
    private final LeaderboardService leaderboardService;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;

    public UserService(UserRepository userRepository, EnrollmentRepository enrollmentRepository,
                       CertificateRepository certificateRepository, QuizAttemptRepository quizAttemptRepository,
                       RewardService rewardService, CourseService courseService,
                       LeaderboardService leaderboardService, PasswordEncoder passwordEncoder, JwtUtils jwtUtils) {
        this.userRepository = userRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.certificateRepository = certificateRepository;
        this.quizAttemptRepository = quizAttemptRepository;
        this.rewardService = rewardService;
        this.courseService = courseService;
        this.leaderboardService = leaderboardService;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtils = jwtUtils;
    }

    public User require(Long userId) {
        return userRepository.findById(userId).orElseThrow(() -> ApiException.notFound("User"));
    }

    @Transactional(readOnly = true)
    public ProfileResponse profile(Long userId) {
        User user = require(userId);
        var myCourses = courseService.myCourses(userId);
        long completed = myCourses.stream().filter(c -> c.progress().percentage() >= 100).count();
        long quizzesPassed = quizAttemptRepository.findByUserId(userId).stream()
                .filter(a -> a.isPassed()).map(a -> a.getQuiz().getId()).distinct().count();
        var rewards = rewardService.statusFor(userId);
        return new ProfileResponse(
                user.getId(), user.getFullName(), user.getEmail(), user.getRole(), user.getCreatedAt(),
                myCourses.size(), completed, certificateRepository.findByUserIdWithCourse(userId).size(),
                rewards.problemsSolved(), quizzesPassed, leaderboardService.pointsFor(userId), rewards);
    }

    @Transactional
    public UserInfo updateProfile(Long userId, UpdateProfileRequest req) {
        User user = require(userId);
        user.setFullName(req.fullName().trim());
        userRepository.save(user);
        return AuthService.toInfo(user);
    }

    /** Changes the password, signs out other devices, and returns a fresh token for this one. */
    @Transactional
    public LoginResponse changePassword(Long userId, ChangePasswordRequest req) {
        User user = require(userId);
        if (!passwordEncoder.matches(req.currentPassword(), user.getPassword())) {
            throw ApiException.badRequest("Current password is incorrect");
        }
        if (passwordEncoder.matches(req.newPassword(), user.getPassword())) {
            throw ApiException.badRequest("New password must be different from the current one");
        }
        user.setPassword(passwordEncoder.encode(req.newPassword()));
        user.setPasswordChangedAt(LocalDateTime.now().truncatedTo(ChronoUnit.SECONDS));
        userRepository.save(user);
        return new LoginResponse(jwtUtils.generateToken(user.getId(), user.getEmail(), user.getRole()), AuthService.toInfo(user));
    }
}
