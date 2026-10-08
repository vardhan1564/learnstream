package com.learnsstream.controller;

import com.learnsstream.dto.ProblemDtos.*;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.ProblemService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/problems")
public class ProblemController {

    private final ProblemService problemService;

    public ProblemController(ProblemService problemService) {
        this.problemService = problemService;
    }

    @GetMapping
    public List<ProblemSummary> list() {
        return problemService.list(CurrentUser.getOrNull());
    }

    @GetMapping("/languages")
    public List<LanguageInfo> languages() {
        return problemService.languages();
    }

    /** Sample test cases only - hidden tests stay on the server. */
    @GetMapping("/{id}")
    public ProblemDetail detail(@PathVariable Long id) {
        return problemService.detail(id, CurrentUser.getOrNull());
    }

    @PostMapping("/{id}/run")
    public RunResponse run(@PathVariable Long id, @Valid @RequestBody RunRequest req) {
        return problemService.run(id, req, CurrentUser.get());
    }

    @PostMapping("/{id}/submit")
    public RunResponse submit(@PathVariable Long id, @Valid @RequestBody RunRequest req) {
        return problemService.submit(id, req, CurrentUser.get());
    }

    @GetMapping("/{id}/submissions")
    public List<SubmissionView> history(@PathVariable Long id) {
        return problemService.history(id, CurrentUser.get());
    }
}
