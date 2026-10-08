package com.learnsstream.repository;

import com.learnsstream.entity.Roadmap;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RoadmapRepository extends JpaRepository<Roadmap, Long> {

    List<Roadmap> findByPublishedTrueOrderByCreatedAtDesc();

    List<Roadmap> findAllByOrderByCreatedAtDesc();
}
