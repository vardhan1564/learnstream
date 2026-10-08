package com.learnsstream.service;

import com.learnsstream.dto.RewardDtos.RewardStatus;
import com.learnsstream.entity.Enrollment;
import com.learnsstream.repository.EnrollmentRepository;
import com.learnsstream.repository.SubmissionRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Rule: every N distinct solved problems (default 5) = 1 free course credit. */
@Service
public class RewardService {

    private final SubmissionRepository submissionRepository;
    private final EnrollmentRepository enrollmentRepository;

    @Value("${learnstream.reward.problems-per-free-course:5}")
    private int problemsPerFreeCourse;

    public RewardService(SubmissionRepository submissionRepository, EnrollmentRepository enrollmentRepository) {
        this.submissionRepository = submissionRepository;
        this.enrollmentRepository = enrollmentRepository;
    }

    @Transactional(readOnly = true)
    public RewardStatus statusFor(Long userId) {
        int per = Math.max(1, problemsPerFreeCourse);
        long solved = submissionRepository.countSolvedProblems(userId);
        long earned = solved / per;
        long used = enrollmentRepository.countByUserIdAndSource(userId, Enrollment.SOURCE_REWARD);
        long available = Math.max(0, earned - used);
        long toNext = per - (solved % per);
        return new RewardStatus(solved, per, earned, used, available, toNext);
    }
}
