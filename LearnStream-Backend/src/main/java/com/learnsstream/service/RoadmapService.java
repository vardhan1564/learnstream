package com.learnsstream.service;

import com.learnsstream.dto.MiscDtos.*;
import com.learnsstream.entity.*;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.*;
import com.learnsstream.security.AuthUser;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class RoadmapService {

    private final RoadmapRepository roadmapRepository;
    private final RoadmapStepRepository stepRepository;
    private final RoadmapProgressRepository progressRepository;
    private final UserRepository userRepository;
    private final CourseService courseService;

    public RoadmapService(RoadmapRepository roadmapRepository, RoadmapStepRepository stepRepository,
                          RoadmapProgressRepository progressRepository, UserRepository userRepository,
                          CourseService courseService) {
        this.roadmapRepository = roadmapRepository;
        this.stepRepository = stepRepository;
        this.progressRepository = progressRepository;
        this.userRepository = userRepository;
        this.courseService = courseService;
    }

    @Transactional(readOnly = true)
    public List<RoadmapSummary> list(AuthUser viewer) {
        Set<Long> done = completed(viewer);
        return roadmapRepository.findByPublishedTrueOrderByCreatedAtDesc().stream()
                .map(r -> summary(r, done))
                .toList();
    }

    @Transactional(readOnly = true)
    public RoadmapDetail detail(Long id, AuthUser viewer) {
        Roadmap r = require(id);
        if (!r.isPublished() && (viewer == null || !viewer.isAdmin())) {
            throw ApiException.notFound("Roadmap");
        }
        return detailView(r, completed(viewer));
    }

    /** Ticks / unticks a step for the current student. */
    @Transactional
    public RoadmapDetail toggleStep(Long stepId, AuthUser viewer) {
        RoadmapStep step = stepRepository.findById(stepId).orElseThrow(() -> ApiException.notFound("Step"));
        if (!step.getRoadmap().isPublished() && !viewer.isAdmin()) {
            throw ApiException.notFound("Step");
        }
        Optional<RoadmapProgress> existing = progressRepository.findByUserIdAndStepId(viewer.id(), stepId);
        if (existing.isPresent()) {
            progressRepository.delete(existing.get());
        } else {
            RoadmapProgress p = new RoadmapProgress();
            p.setUser(userRepository.getReferenceById(viewer.id()));
            p.setStep(step);
            progressRepository.save(p);
        }
        progressRepository.flush();
        return detailView(step.getRoadmap(), completed(viewer));
    }

    // ---------- Admin ----------

    @Transactional(readOnly = true)
    public List<RoadmapDetail> adminList() {
        return roadmapRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(r -> detailView(r, Set.of()))
                .toList();
    }

    @Transactional
    public RoadmapDetail create(RoadmapRequest req) {
        Roadmap r = new Roadmap();
        apply(r, req);
        return detailView(roadmapRepository.save(r), Set.of());
    }

    @Transactional
    public RoadmapDetail update(Long id, RoadmapRequest req) {
        Roadmap r = require(id);
        apply(r, req);
        return detailView(roadmapRepository.save(r), Set.of());
    }

    @Transactional
    public void delete(Long id) {
        Roadmap r = require(id);
        progressRepository.deleteByRoadmapId(id);
        roadmapRepository.delete(r);
    }

    private void apply(Roadmap r, RoadmapRequest req) {
        r.setTitle(req.title().trim());
        r.setDescription(CourseService.blankToNull(req.description()));
        r.setLevel(CourseService.blankToNull(req.level()));
        r.setDuration(CourseService.blankToNull(req.duration()));
        if (req.published() != null) {
            r.setPublished(req.published());
        }

        Map<Long, RoadmapStep> existing = r.getSteps().stream()
                .filter(s -> s.getId() != null)
                .collect(Collectors.toMap(RoadmapStep::getId, s -> s));
        Set<Long> kept = new HashSet<>();
        List<RoadmapStep> steps = new ArrayList<>();
        for (int i = 0; i < req.steps().size(); i++) {
            RoadmapStepRequest sr = req.steps().get(i);
            RoadmapStep step = sr.id() != null && existing.containsKey(sr.id()) && !kept.contains(sr.id())
                    ? existing.get(sr.id()) : new RoadmapStep();
            if (step.getId() != null) kept.add(step.getId());
            step.setRoadmap(r);
            step.setTitle(sr.title().trim());
            step.setDescription(CourseService.blankToNull(sr.description()));
            step.setResourceUrl(CourseService.blankToNull(sr.resourceUrl()));
            step.setCourse(sr.courseId() == null ? null : courseService.requireCourse(sr.courseId()));
            step.setPosition(i);
            steps.add(step);
        }
        Set<Long> removed = new HashSet<>(existing.keySet());
        removed.removeAll(kept);
        if (!removed.isEmpty()) {
            progressRepository.deleteByStepIds(removed);
        }
        r.getSteps().clear();
        r.getSteps().addAll(steps);
    }

    private Set<Long> completed(AuthUser viewer) {
        return viewer == null ? Set.of() : new HashSet<>(progressRepository.findCompletedStepIds(viewer.id()));
    }

    private RoadmapSummary summary(Roadmap r, Set<Long> done) {
        int completed = (int) r.getSteps().stream().filter(s -> done.contains(s.getId())).count();
        return new RoadmapSummary(r.getId(), r.getTitle(), r.getDescription(), r.getLevel(), r.getDuration(),
                r.getSteps().size(), completed, r.isPublished());
    }

    private RoadmapDetail detailView(Roadmap r, Set<Long> done) {
        List<RoadmapStepView> steps = r.getSteps().stream()
                .map(s -> new RoadmapStepView(s.getId(), s.getTitle(), s.getDescription(), s.getResourceUrl(),
                        s.getCourse() == null ? null : s.getCourse().getId(),
                        s.getCourse() == null ? null : s.getCourse().getTitle(),
                        s.getPosition(), done.contains(s.getId())))
                .toList();
        return new RoadmapDetail(summary(r, done), steps);
    }

    private Roadmap require(Long id) {
        return roadmapRepository.findById(id).orElseThrow(() -> ApiException.notFound("Roadmap"));
    }
}
