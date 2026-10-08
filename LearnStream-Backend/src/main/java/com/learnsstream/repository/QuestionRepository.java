package com.learnsstream.repository;

import com.learnsstream.entity.Question;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface QuestionRepository extends JpaRepository<Question, Long> {

    /** Returns [quizId, questionCount] pairs. */
    @Query("SELECT q.quiz.id, COUNT(q) FROM Question q GROUP BY q.quiz.id")
    List<Object[]> countPerQuiz();
}
