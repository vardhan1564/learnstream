package com.learnsstream.service;

import com.learnsstream.dto.MiscDtos.LeaderboardEntry;
import com.learnsstream.entity.Role;
import com.learnsstream.entity.User;
import com.learnsstream.repository.QuizAttemptRepository;
import com.learnsstream.repository.SubmissionRepository;
import com.learnsstream.repository.UserRepository;
import com.learnsstream.security.AuthUser;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * Points: EASY = 10, MEDIUM = 20, HARD = 40 per distinct solved problem,
 * plus 2 points per correct answer in each quiz's best attempt.
 */
@Service
public class LeaderboardService {

    public static final int EASY_POINTS = 10;
    public static final int MEDIUM_POINTS = 20;
    public static final int HARD_POINTS = 40;
    public static final int QUIZ_POINTS_PER_CORRECT = 2;

    private final UserRepository userRepository;
    private final SubmissionRepository submissionRepository;
    private final QuizAttemptRepository quizAttemptRepository;

    public LeaderboardService(UserRepository userRepository, SubmissionRepository submissionRepository,
                              QuizAttemptRepository quizAttemptRepository) {
        this.userRepository = userRepository;
        this.submissionRepository = submissionRepository;
        this.quizAttemptRepository = quizAttemptRepository;
    }

    private static final class Tally {
        long solved, hard, problemPoints, quizPoints;
        long total() { return problemPoints + quizPoints; }
    }

    /**
     * @param includeEmails true only for admins
     * @return top `limit` students, plus the viewer's own row at the end if they're outside the top
     */
    @Transactional(readOnly = true)
    public List<LeaderboardEntry> leaderboard(int limit, AuthUser viewer, boolean includeEmails) {
        Map<Long, Tally> tallies = computeTallies();
        List<User> students = userRepository.findByRole(Role.STUDENT);

        List<User> ranked = students.stream()
                .filter(User::isVerified)
                .filter(u -> tallies.containsKey(u.getId()) && tallies.get(u.getId()).total() > 0)
                .sorted(Comparator.<User>comparingLong(u -> tallies.get(u.getId()).total()).reversed()
                        .thenComparing(Comparator.comparingLong((User u) -> tallies.get(u.getId()).hard).reversed())
                        .thenComparing(User::getCreatedAt))
                .toList();

        List<LeaderboardEntry> result = new ArrayList<>();
        int max = Math.min(Math.max(limit, 1), 500);
        for (int i = 0; i < ranked.size(); i++) {
            User u = ranked.get(i);
            boolean me = viewer != null && viewer.id().equals(u.getId());
            if (i < max) {
                result.add(entry(i + 1, u, tallies.get(u.getId()), includeEmails, me));
            } else if (me) {
                result.add(entry(i + 1, u, tallies.get(u.getId()), includeEmails, true));
            }
        }
        return result;
    }

    @Transactional(readOnly = true)
    public long pointsFor(Long userId) {
        Tally t = computeTallies().get(userId);
        return t == null ? 0 : t.total();
    }

    private Map<Long, Tally> computeTallies() {
        Map<Long, Tally> map = new HashMap<>();
        for (Object[] row : submissionRepository.findAllSolved()) {
            Long userId = ((Number) row[0]).longValue();
            String difficulty = row[2] == null ? "EASY" : row[2].toString();
            Tally t = map.computeIfAbsent(userId, k -> new Tally());
            t.solved++;
            switch (difficulty) {
                case "HARD" -> { t.hard++; t.problemPoints += HARD_POINTS; }
                case "MEDIUM" -> t.problemPoints += MEDIUM_POINTS;
                default -> t.problemPoints += EASY_POINTS;
            }
        }
        for (Object[] row : quizAttemptRepository.bestScoresPerUserAndQuiz()) {
            Long userId = ((Number) row[0]).longValue();
            long best = row[2] == null ? 0 : ((Number) row[2]).longValue();
            map.computeIfAbsent(userId, k -> new Tally()).quizPoints += best * QUIZ_POINTS_PER_CORRECT;
        }
        return map;
    }

    private static LeaderboardEntry entry(int rank, User u, Tally t, boolean includeEmails, boolean me) {
        return new LeaderboardEntry(rank, u.getId(), u.getFullName(), includeEmails ? u.getEmail() : null,
                t.solved, t.hard, t.quizPoints, t.total(), me);
    }
}
