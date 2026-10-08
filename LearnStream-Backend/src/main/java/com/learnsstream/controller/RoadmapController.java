package com.learnsstream.controller;

import com.learnsstream.dto.MiscDtos.RoadmapDetail;
import com.learnsstream.dto.MiscDtos.RoadmapSummary;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.RoadmapService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/roadmaps")
public class RoadmapController {

    private final RoadmapService roadmapService;

    public RoadmapController(RoadmapService roadmapService) {
        this.roadmapService = roadmapService;
    }

    @GetMapping
    public List<RoadmapSummary> list() {
        return roadmapService.list(CurrentUser.getOrNull());
    }

    @GetMapping("/{id}")
    public RoadmapDetail detail(@PathVariable Long id) {
        return roadmapService.detail(id, CurrentUser.getOrNull());
    }

    @PostMapping("/steps/{stepId}/toggle")
    public RoadmapDetail toggle(@PathVariable Long stepId) {
        return roadmapService.toggleStep(stepId, CurrentUser.get());
    }
}
