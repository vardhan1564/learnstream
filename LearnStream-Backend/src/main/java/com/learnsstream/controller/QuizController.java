package com.learnsstream.controller;

import com.learnsstream.dto.QuizDtos.*;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.QuizService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/quizzes")
public class QuizController {

    private final QuizService quizService;

    public QuizController(QuizService quizService) {
        this.quizService = quizService;
    }

    @GetMapping
    public List<QuizSummary> list() {
        return quizService.list(CurrentUser.get());
    }

    /** Questions and options only - correct answers are never sent. */
    @GetMapping("/{id}")
    public QuizForStudent get(@PathVariable Long id) {
        return quizService.getForStudent(id, CurrentUser.get());
    }

    @PostMapping("/{id}/submit")
    public QuizResult submit(@PathVariable Long id, @Valid @RequestBody SubmitQuizRequest req) {
        return quizService.submit(id, req.answers(), CurrentUser.get());
    }
}
