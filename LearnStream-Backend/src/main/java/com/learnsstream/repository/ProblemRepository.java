package com.learnsstream.repository;

import com.learnsstream.entity.Problem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface ProblemRepository extends JpaRepository<Problem, Long> {

    List<Problem> findByPublishedTrueOrderByIdAsc();

    List<Problem> findAllByOrderByIdDesc();

    @Query("SELECT p.title FROM Problem p")
    List<String> findAllTitles();
}
