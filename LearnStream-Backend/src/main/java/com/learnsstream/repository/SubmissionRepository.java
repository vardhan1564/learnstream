package com.learnsstream.repository;

import com.learnsstream.entity.Submission;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface SubmissionRepository extends JpaRepository<Submission, Long> {

    @Query("SELECT s FROM Submission s WHERE s.user.id = :userId AND s.problem.id = :problemId ORDER BY s.submittedAt DESC")
    List<Submission> findHistory(@Param("userId") Long userId, @Param("problemId") Long problemId, Pageable pageable);

    boolean existsByUserIdAndProblemIdAndStatus(Long userId, Long problemId, String status);

    @Query("SELECT DISTINCT s.problem.id FROM Submission s WHERE s.user.id = :userId AND s.status = 'ACCEPTED'")
    List<Long> findSolvedProblemIds(@Param("userId") Long userId);

    @Query("SELECT COUNT(DISTINCT s.problem.id) FROM Submission s WHERE s.user.id = :userId AND s.status = 'ACCEPTED'")
    long countSolvedProblems(@Param("userId") Long userId);

    /** [userId, problemId, difficulty] - one row per distinct solved problem (leaderboard) */
    @Query("SELECT DISTINCT s.user.id, s.problem.id, s.problem.difficulty FROM Submission s WHERE s.status = 'ACCEPTED'")
    List<Object[]> findAllSolved();

    long countByStatus(String status);

    @Modifying
    @Query("DELETE FROM Submission s WHERE s.problem.id = :problemId")
    void deleteByProblemId(@Param("problemId") Long problemId);
}
