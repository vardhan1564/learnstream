package com.learnsstream.repository;

import com.learnsstream.entity.Lesson;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface LessonRepository extends JpaRepository<Lesson, Long> {

    long countByCourseId(Long courseId);

    /** Returns [courseId, lessonCount] pairs - one query for the whole course list. */
    @Query("SELECT l.course.id, COUNT(l) FROM Lesson l GROUP BY l.course.id")
    List<Object[]> countLessonsPerCourse();

    @Query("SELECT l.course.id, COALESCE(SUM(l.durationMinutes), 0) FROM Lesson l GROUP BY l.course.id")
    List<Object[]> sumDurationPerCourse();
}
