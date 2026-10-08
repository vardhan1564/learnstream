package com.learnsstream.repository;

import com.learnsstream.entity.Problem;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ProblemRepository extends JpaRepository<Problem, Long> {

    List<Problem> findByPublishedTrueOrderByIdAsc();

    List<Problem> findAllByOrderByIdDesc();
}
