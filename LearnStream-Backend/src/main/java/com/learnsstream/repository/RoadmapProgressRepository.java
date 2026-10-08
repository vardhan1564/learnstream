package com.learnsstream.repository;

import com.learnsstream.entity.RoadmapProgress;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface RoadmapProgressRepository extends JpaRepository<RoadmapProgress, Long> {

    Optional<RoadmapProgress> findByUserIdAndStepId(Long userId, Long stepId);

    @Query("SELECT p.step.id FROM RoadmapProgress p WHERE p.user.id = :userId")
    List<Long> findCompletedStepIds(@Param("userId") Long userId);

    @Modifying
    @Query("DELETE FROM RoadmapProgress p WHERE p.step.id IN :stepIds")
    void deleteByStepIds(@Param("stepIds") Collection<Long> stepIds);

    @Modifying
    @Query("DELETE FROM RoadmapProgress p WHERE p.step.id IN (SELECT s.id FROM RoadmapStep s WHERE s.roadmap.id = :roadmapId)")
    void deleteByRoadmapId(@Param("roadmapId") Long roadmapId);
}
