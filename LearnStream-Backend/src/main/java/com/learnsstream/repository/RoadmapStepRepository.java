package com.learnsstream.repository;

import com.learnsstream.entity.RoadmapStep;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface RoadmapStepRepository extends JpaRepository<RoadmapStep, Long> {

    @Modifying
    @Query("UPDATE RoadmapStep s SET s.course = NULL WHERE s.course.id = :courseId")
    void detachFromCourse(@Param("courseId") Long courseId);
}
