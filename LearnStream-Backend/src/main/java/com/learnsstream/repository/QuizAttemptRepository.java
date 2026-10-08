package com.learnsstream.repository;

import com.learnsstream.entity.QuizAttempt;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface QuizAttemptRepository extends JpaRepository<QuizAttempt, Long> {

    long countByUserIdAndQuizId(Long userId, Long quizId);

    boolean existsByUserIdAndQuizIdAndPassedTrue(Long userId, Long quizId);

    @Query("SELECT a FROM QuizAttempt a WHERE a.user.id = :userId ORDER BY a.attemptedAt DESC")
    List<QuizAttempt> findByUserId(@Param("userId") Long userId);

    /** [quizId, attemptCount, bestPercentage] for one user */
    @Query("SELECT a.quiz.id, COUNT(a), MAX(a.percentage) FROM QuizAttempt a WHERE a.user.id = :userId GROUP BY a.quiz.id")
    List<Object[]> statsForUser(@Param("userId") Long userId);

    /** [userId, quizId, bestScore] for the leaderboard */
    @Query("SELECT a.user.id, a.quiz.id, MAX(a.score) FROM QuizAttempt a GROUP BY a.user.id, a.quiz.id")
    List<Object[]> bestScoresPerUserAndQuiz();

    @Modifying
    @Query("DELETE FROM QuizAttempt a WHERE a.quiz.id = :quizId")
    void deleteByQuizId(@Param("quizId") Long quizId);
}
