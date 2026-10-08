package com.learnsstream.repository;

import com.learnsstream.entity.Enrollment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {

    boolean existsByUserIdAndCourseId(Long userId, Long courseId);

    long countByCourseId(Long courseId);

    long countByUserIdAndSource(Long userId, String source);

    @Query("SELECT e.course.id FROM Enrollment e WHERE e.user.id = :userId")
    List<Long> findCourseIdsByUserId(@Param("userId") Long userId);

    @Query("SELECT e FROM Enrollment e JOIN FETCH e.course WHERE e.user.id = :userId ORDER BY e.enrolledAt DESC")
    List<Enrollment> findByUserIdWithCourse(@Param("userId") Long userId);

    @Query("SELECT e.course.title FROM Enrollment e WHERE e.user.id = :userId")
    List<String> findCourseTitlesByUserId(@Param("userId") Long userId);
}
