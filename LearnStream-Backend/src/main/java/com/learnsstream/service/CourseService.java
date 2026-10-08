package com.learnsstream.service;

import com.learnsstream.dto.CourseDtos.*;
import com.learnsstream.entity.*;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.*;
import com.learnsstream.security.AuthUser;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class CourseService {

    private final CourseRepository courseRepository;
    private final LessonRepository lessonRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final LessonProgressRepository lessonProgressRepository;
    private final QuizRepository quizRepository;
    private final QuizAttemptRepository quizAttemptRepository;
    private final CertificateRepository certificateRepository;
    private final PaymentRepository paymentRepository;
    private final RoadmapStepRepository roadmapStepRepository;
    private final UserRepository userRepository;
    private final VideoStorageService videoStorage;

    @Value("${learnstream.certificate.require-quiz-pass:true}")
    private boolean requireQuizPass;

    public CourseService(CourseRepository courseRepository, LessonRepository lessonRepository,
                         EnrollmentRepository enrollmentRepository, LessonProgressRepository lessonProgressRepository,
                         QuizRepository quizRepository, QuizAttemptRepository quizAttemptRepository,
                         CertificateRepository certificateRepository, PaymentRepository paymentRepository,
                         RoadmapStepRepository roadmapStepRepository, UserRepository userRepository,
                         VideoStorageService videoStorage) {
        this.courseRepository = courseRepository;
        this.lessonRepository = lessonRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.lessonProgressRepository = lessonProgressRepository;
        this.quizRepository = quizRepository;
        this.quizAttemptRepository = quizAttemptRepository;
        this.certificateRepository = certificateRepository;
        this.paymentRepository = paymentRepository;
        this.roadmapStepRepository = roadmapStepRepository;
        this.userRepository = userRepository;
        this.videoStorage = videoStorage;
    }

    // ======================= Student / public =======================

    @Transactional(readOnly = true)
    public List<CourseSummary> listPublished(AuthUser viewer) {
        Set<Long> enrolled = viewer == null ? Set.of() : new HashSet<>(enrollmentRepository.findCourseIdsByUserId(viewer.id()));
        Map<Long, Long> lessonCounts = toMap(lessonRepository.countLessonsPerCourse());
        Map<Long, Long> minutes = toMap(lessonRepository.sumDurationPerCourse());
        return courseRepository.findByPublishedTrueOrderByCreatedAtDesc().stream()
                .map(c -> summary(c, lessonCounts.getOrDefault(c.getId(), 0L), minutes.getOrDefault(c.getId(), 0L),
                        enrolled.contains(c.getId())))
                .toList();
    }

    @Transactional(readOnly = true)
    public CourseDetail detail(Long courseId, AuthUser viewer) {
        Course course = requireCourse(courseId);
        boolean admin = viewer != null && viewer.isAdmin();
        if (!course.isPublished() && !admin) {
            throw ApiException.notFound("Course");
        }
        boolean enrolled = viewer != null && enrollmentRepository.existsByUserIdAndCourseId(viewer.id(), courseId);
        boolean canWatch = enrolled || admin;

        Set<Long> completed = enrolled
                ? new HashSet<>(lessonProgressRepository.findCompletedLessonIds(viewer.id(), courseId))
                : Set.of();

        List<LessonView> lessons = course.getLessons().stream()
                .map(l -> lessonView(l, canWatch || l.isPreview(), completed.contains(l.getId()), admin))
                .toList();

        List<Quiz> quizzes = quizRepository.findByCourseIdAndPublishedTrue(courseId);
        List<QuizBrief> quizBriefs = quizzes.stream()
                .map(q -> new QuizBrief(q.getId(), q.getTitle(), q.getQuestions().size(), q.getPassPercentage(),
                        viewer != null && quizAttemptRepository.existsByUserIdAndQuizIdAndPassedTrue(viewer.id(), q.getId())))
                .toList();

        CourseProgress progress = enrolled ? progress(viewer.id(), course) : null;
        return new CourseDetail(summary(course, lessons.size(), totalMinutes(course), enrolled), lessons, quizBriefs, progress);
    }

    /** Marks a lesson complete for an enrolled student (safe to call twice). */
    @Transactional
    public CourseProgress completeLesson(Long lessonId, AuthUser viewer) {
        Lesson lesson = lessonRepository.findById(lessonId).orElseThrow(() -> ApiException.notFound("Lesson"));
        Course course = lesson.getCourse();
        if (!enrollmentRepository.existsByUserIdAndCourseId(viewer.id(), course.getId())) {
            throw ApiException.forbidden("Enroll in this course to track your progress");
        }
        if (!lessonProgressRepository.existsByUserIdAndLessonId(viewer.id(), lessonId)) {
            LessonProgress progress = new LessonProgress();
            progress.setUser(userRepository.getReferenceById(viewer.id()));
            progress.setLesson(lesson);
            lessonProgressRepository.save(progress);
            lessonProgressRepository.flush();
        }
        return progress(viewer.id(), course);
    }

    @Transactional(readOnly = true)
    public CourseProgress progressFor(Long courseId, AuthUser viewer) {
        Course course = requireCourse(courseId);
        if (!enrollmentRepository.existsByUserIdAndCourseId(viewer.id(), courseId)) {
            throw ApiException.forbidden("You are not enrolled in this course");
        }
        return progress(viewer.id(), course);
    }

    @Transactional(readOnly = true)
    public List<MyCourse> myCourses(Long userId) {
        return enrollmentRepository.findByUserIdWithCourse(userId).stream()
                .map(e -> {
                    Course c = e.getCourse();
                    return new MyCourse(summary(c, c.getLessons().size(), totalMinutes(c), true),
                            progress(userId, c), e.getSource(), e.getEnrolledAt());
                })
                .toList();
    }

    /**
     * Certificate rule: every lesson completed AND (if enabled) every published quiz of the course passed.
     */
    public CourseProgress progress(Long userId, Course course) {
        List<Long> done = lessonProgressRepository.findCompletedLessonIds(userId, course.getId());
        long total = course.getLessons().size();
        long completed = done.size();
        int percentage = total == 0 ? 0 : (int) Math.min(100, Math.round(completed * 100.0 / total));

        List<Quiz> quizzes = quizRepository.findByCourseIdAndPublishedTrue(course.getId());
        long quizzesPassed = quizzes.stream()
                .filter(q -> quizAttemptRepository.existsByUserIdAndQuizIdAndPassedTrue(userId, q.getId()))
                .count();

        boolean lessonsDone = total > 0 && completed >= total;
        boolean quizzesDone = !requireQuizPass || quizzesPassed >= quizzes.size();
        String serial = certificateRepository.findByUserIdAndCourseId(userId, course.getId())
                .map(Certificate::getSerialNumber).orElse(null);

        return new CourseProgress(done, completed, total, percentage, quizzesPassed, quizzes.size(),
                lessonsDone && quizzesDone, serial);
    }

    public Course requireCourse(Long id) {
        return courseRepository.findById(id).orElseThrow(() -> ApiException.notFound("Course"));
    }

    // ======================= Admin =======================

    @Transactional(readOnly = true)
    public List<AdminCourseView> adminList() {
        return courseRepository.findAllByOrderByCreatedAtDesc().stream().map(this::adminView).toList();
    }

    @Transactional(readOnly = true)
    public AdminCourseView adminGet(Long id) {
        return adminView(requireCourse(id));
    }

    @Transactional
    public AdminCourseView create(CourseRequest req) {
        Course course = new Course();
        apply(course, req);
        mergeLessons(course, req.lessons());
        return adminView(courseRepository.save(course));
    }

    @Transactional
    public AdminCourseView update(Long id, CourseRequest req) {
        Course course = requireCourse(id);
        apply(course, req);
        mergeLessons(course, req.lessons());
        return adminView(courseRepository.save(course));
    }

    @Transactional
    public void delete(Long id) {
        Course course = requireCourse(id);
        long enrollments = enrollmentRepository.countByCourseId(id);
        if (enrollments > 0) {
            throw ApiException.conflict(enrollments + " student(s) are enrolled in this course, so it can't be deleted. "
                    + "Unpublish it instead to hide it from the catalog.");
        }
        lessonProgressRepository.deleteByCourseId(id);
        paymentRepository.deleteUnpaidByCourseId(id);
        quizRepository.detachFromCourse(id);
        roadmapStepRepository.detachFromCourse(id);
        List<String> files = course.getLessons().stream().map(Lesson::getVideoFileKey).filter(Objects::nonNull).toList();
        courseRepository.delete(course);
        deleteFilesAfterCommit(files);
    }

    private void apply(Course course, CourseRequest req) {
        course.setTitle(req.title().trim());
        course.setDescription(blankToNull(req.description()));
        course.setPrice(Math.round(req.price() * 100) / 100.0);
        course.setThumbnail(blankToNull(req.thumbnail()));
        course.setCategory(blankToNull(req.category()));
        course.setLevel(blankToNull(req.level()));
        course.setInstructor(blankToNull(req.instructor()));
        if (req.published() != null) {
            course.setPublished(req.published());
        }
    }

    /** Updates lessons in place (matched by id) so students keep their progress on unchanged lessons. */
    private void mergeLessons(Course course, List<LessonRequest> requests) {
        List<LessonRequest> incoming = requests == null ? List.of() : requests;
        Map<Long, Lesson> existing = course.getLessons().stream()
                .filter(l -> l.getId() != null)
                .collect(Collectors.toMap(Lesson::getId, l -> l));

        List<Lesson> result = new ArrayList<>();
        Set<Long> kept = new HashSet<>();
        List<String> replacedFiles = new ArrayList<>();
        for (int i = 0; i < incoming.size(); i++) {
            LessonRequest r = incoming.get(i);
            Lesson lesson = (r.id() != null && existing.containsKey(r.id())) ? existing.get(r.id()) : new Lesson();
            if (lesson.getId() != null) {
                if (!kept.add(lesson.getId())) {
                    lesson = new Lesson(); // same id sent twice - treat the duplicate as a new lesson
                }
            }
            String url = blankToNull(r.videoUrl());
            String fileKey = blankToNull(r.videoFileKey());
            if (url == null && fileKey == null) {
                throw ApiException.badRequest("Lesson " + (i + 1) + " needs a video: paste a link or upload a file");
            }
            if (fileKey != null) {
                url = null; // an uploaded file wins over a link
            }
            if (lesson.getVideoFileKey() != null && !lesson.getVideoFileKey().equals(fileKey)) {
                replacedFiles.add(lesson.getVideoFileKey()); // video replaced or switched to a link
            }
            lesson.setTitle(r.title().trim());
            lesson.setDescription(blankToNull(r.description()));
            lesson.setVideoUrl(url);
            lesson.setVideoFileKey(fileKey);
            lesson.setVideoFileName(fileKey == null ? null : blankToNull(r.videoFileName()));
            lesson.setDurationMinutes(r.durationMinutes());
            lesson.setPreview(Boolean.TRUE.equals(r.preview()));
            lesson.setPosition(i);
            lesson.setCourse(course);
            result.add(lesson);
        }

        Set<Long> removed = new HashSet<>(existing.keySet());
        removed.removeAll(kept);
        if (!removed.isEmpty()) {
            lessonProgressRepository.deleteByLessonIds(removed);
            removed.forEach(rid -> {
                String key = existing.get(rid).getVideoFileKey();
                if (key != null) replacedFiles.add(key);
            });
        }
        course.getLessons().clear();
        course.getLessons().addAll(result);
        Set<String> stillUsed = result.stream().map(Lesson::getVideoFileKey).filter(Objects::nonNull).collect(Collectors.toSet());
        deleteFilesAfterCommit(replacedFiles.stream().filter(k -> !stillUsed.contains(k)).toList());
    }

    private AdminCourseView adminView(Course c) {
        List<LessonView> lessons = c.getLessons().stream().map(l -> lessonView(l, true, false, true)).toList();
        CourseSummary s = summary(c, lessons.size(), totalMinutes(c), false);
        return new AdminCourseView(s, lessons, c.getId() == null ? 0 : enrollmentRepository.countByCourseId(c.getId()));
    }

    // ======================= Mapping helpers =======================

    CourseSummary summary(Course c, long lessonCount, long minutes, boolean enrolled) {
        return new CourseSummary(c.getId(), c.getTitle(), c.getDescription(), c.getPrice(), c.getThumbnail(),
                c.getCategory(), c.getLevel(), c.getInstructor(), lessonCount, minutes, c.isPublished(), enrolled);
    }

    private LessonView lessonView(Lesson l, boolean unlocked, boolean completed, boolean forAdmin) {
        boolean uploaded = l.getVideoFileKey() != null;
        // Uploaded videos get a fresh short-lived signed link each time; nothing is sent for locked lessons.
        String url = !unlocked ? null : uploaded ? videoStorage.playbackUrl(l.getVideoFileKey()) : l.getVideoUrl();
        return new LessonView(l.getId(), l.getTitle(), l.getDescription(), url, uploaded ? "UPLOAD" : "LINK",
                l.getDurationMinutes(), l.getPosition(), l.isPreview(), !unlocked, completed,
                forAdmin ? l.getVideoFileKey() : null, forAdmin ? l.getVideoFileName() : null);
    }

    /** Deletes stored files only once the database change is committed (nothing is lost if saving fails). */
    private void deleteFilesAfterCommit(List<String> keys) {
        if (keys.isEmpty()) return;
        if (TransactionSynchronizationManager.isSynchronizationActive()) {
            TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    keys.forEach(videoStorage::delete);
                }
            });
        } else {
            keys.forEach(videoStorage::delete);
        }
    }

    private long totalMinutes(Course c) {
        return c.getLessons().stream().mapToLong(l -> l.getDurationMinutes() == null ? 0 : l.getDurationMinutes()).sum();
    }

    private static Map<Long, Long> toMap(List<Object[]> rows) {
        Map<Long, Long> map = new HashMap<>();
        for (Object[] row : rows) {
            map.put(((Number) row[0]).longValue(), ((Number) row[1]).longValue());
        }
        return map;
    }

    static String blankToNull(String s) {
        return (s == null || s.isBlank()) ? null : s.trim();
    }
}
