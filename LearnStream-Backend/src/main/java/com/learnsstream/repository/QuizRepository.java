package com.learnsstream.repository;

import com.learnsstream.entity.Quiz;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface QuizRepository extends JpaRepository<Quiz, Long> {

    List<Quiz> findByPublishedTrueOrderByCreatedAtDesc();

    List<Quiz> findAllByOrderByCreatedAtDesc();

    List<Quiz> findByCourseIdAndPublishedTrue(Long courseId);

    @Modifying
    @Query("UPDATE Quiz q SET q.course = NULL WHERE q.course.id = :courseId")
    void detachFromCourse(@Param("courseId") Long courseId);
}
