package com.learnsstream.repository;

import com.learnsstream.entity.LessonProgress;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Collection;
import java.util.List;

public interface LessonProgressRepository extends JpaRepository<LessonProgress, Long> {

    boolean existsByUserIdAndLessonId(Long userId, Long lessonId);

    @Query("SELECT lp.lesson.id FROM LessonProgress lp WHERE lp.user.id = :userId AND lp.lesson.course.id = :courseId")
    List<Long> findCompletedLessonIds(@Param("userId") Long userId, @Param("courseId") Long courseId);

    @Query("SELECT COUNT(lp) FROM LessonProgress lp WHERE lp.user.id = :userId AND lp.lesson.course.id = :courseId")
    long countCompleted(@Param("userId") Long userId, @Param("courseId") Long courseId);

    @Modifying
    @Query("DELETE FROM LessonProgress lp WHERE lp.lesson.id IN :lessonIds")
    void deleteByLessonIds(@Param("lessonIds") Collection<Long> lessonIds);

    @Modifying
    @Query("DELETE FROM LessonProgress lp WHERE lp.lesson.id IN (SELECT l.id FROM Lesson l WHERE l.course.id = :courseId)")
    void deleteByCourseId(@Param("courseId") Long courseId);
}
