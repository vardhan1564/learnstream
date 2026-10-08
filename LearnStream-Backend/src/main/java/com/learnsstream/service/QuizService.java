package com.learnsstream.service;

import com.learnsstream.dto.QuizDtos.*;
import com.learnsstream.entity.*;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.*;
import com.learnsstream.security.AuthUser;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * MCQ quizzes. Correct answers are only ever read inside this service (for grading) and in admin DTOs.
 * Students receive questions without answers and get back only their score.
 */
@Service
public class QuizService {

    private final QuizRepository quizRepository;
    private final QuestionRepository questionRepository;
    private final QuizAttemptRepository attemptRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository;
    private final CourseService courseService;

    public QuizService(QuizRepository quizRepository, QuestionRepository questionRepository,
                       QuizAttemptRepository attemptRepository, EnrollmentRepository enrollmentRepository,
                       UserRepository userRepository, CourseService courseService) {
        this.quizRepository = quizRepository;
        this.questionRepository = questionRepository;
        this.attemptRepository = attemptRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.userRepository = userRepository;
        this.courseService = courseService;
    }

    // ======================= Student =======================

    @Transactional(readOnly = true)
    public List<QuizSummary> list(AuthUser viewer) {
        Map<Long, Long> counts = new HashMap<>();
        for (Object[] row : questionRepository.countPerQuiz()) {
            counts.put(((Number) row[0]).longValue(), ((Number) row[1]).longValue());
        }
        Map<Long, Object[]> stats = statsFor(viewer);
        return quizRepository.findByPublishedTrueOrderByCreatedAtDesc().stream()
                .map(q -> summary(q, counts.getOrDefault(q.getId(), 0L).intValue(), stats.get(q.getId()), viewer))
                .filter(s -> s.questionCount() > 0)
                .toList();
    }

    @Transactional(readOnly = true)
    public QuizForStudent getForStudent(Long quizId, AuthUser viewer) {
        Quiz quiz = accessibleQuiz(quizId, viewer);
        List<StudentQuestion> questions = quiz.getQuestions().stream()
                .map(q -> new StudentQuestion(q.getId(), q.getQuestionText(), options(q)))
                .toList();
        return new QuizForStudent(summary(quiz, questions.size(), statsFor(viewer).get(quizId), viewer), questions);
    }

    @Transactional
    public QuizResult submit(Long quizId, Map<Long, String> answers, AuthUser viewer) {
        // Row lock on the user: parallel submissions can't exceed the attempt limit.
        User user = userRepository.lockById(viewer.id()).orElseThrow(() -> ApiException.notFound("User"));
        Quiz quiz = accessibleQuiz(quizId, viewer);
        List<Question> questions = quiz.getQuestions();
        if (questions.isEmpty()) {
            throw ApiException.badRequest("This quiz has no questions yet");
        }
        long used = attemptRepository.countByUserIdAndQuizId(user.getId(), quizId);
        if (quiz.getMaxAttempts() > 0 && used >= quiz.getMaxAttempts()) {
            throw ApiException.forbidden("You have used all " + quiz.getMaxAttempts() + " attempts for this quiz.");
        }

        Map<Long, String> safeAnswers = answers == null ? Map.of() : answers;
        int score = 0;
        for (Question q : questions) {
            String given = safeAnswers.get(q.getId());
            if (given != null && given.trim().equalsIgnoreCase(q.getCorrectOption())) {
                score++;
            }
        }
        int total = questions.size();
        double percentage = Math.round(score * 1000.0 / total) / 10.0;
        boolean passed = percentage >= quiz.getPassPercentage();

        QuizAttempt attempt = new QuizAttempt();
        attempt.setUser(user);
        attempt.setQuiz(quiz);
        attempt.setScore(score);
        attempt.setTotal(total);
        attempt.setPercentage(percentage);
        attempt.setPassed(passed);
        attemptRepository.save(attempt);

        return new QuizResult(score, total, percentage, passed, quiz.getPassPercentage(), used + 1, quiz.getMaxAttempts());
    }

    private Quiz accessibleQuiz(Long quizId, AuthUser viewer) {
        Quiz quiz = requireQuiz(quizId);
        boolean admin = viewer != null && viewer.isAdmin();
        if (!quiz.isPublished() && !admin) {
            throw ApiException.notFound("Quiz");
        }
        if (quiz.getCourse() != null && !admin
                && (viewer == null || !enrollmentRepository.existsByUserIdAndCourseId(viewer.id(), quiz.getCourse().getId()))) {
            throw ApiException.forbidden("Enroll in \"" + quiz.getCourse().getTitle() + "\" to take this quiz");
        }
        return quiz;
    }

    private Map<Long, Object[]> statsFor(AuthUser viewer) {
        Map<Long, Object[]> stats = new HashMap<>();
        if (viewer != null) {
            for (Object[] row : attemptRepository.statsForUser(viewer.id())) {
                stats.put(((Number) row[0]).longValue(), row);
            }
        }
        return stats;
    }

    private QuizSummary summary(Quiz q, int questionCount, Object[] stat, AuthUser viewer) {
        long attempts = stat == null ? 0 : ((Number) stat[1]).longValue();
        Double best = stat == null || stat[2] == null ? null : ((Number) stat[2]).doubleValue();
        boolean passed = best != null && best >= q.getPassPercentage();
        Course c = q.getCourse();
        return new QuizSummary(q.getId(), q.getTitle(), q.getDescription(), q.getCategory(),
                c == null ? null : c.getId(), c == null ? null : c.getTitle(),
                questionCount, q.getPassPercentage(), q.getMaxAttempts(), attempts, best, passed, q.isPublished());
    }

    private static List<Option> options(Question q) {
        List<Option> list = new ArrayList<>();
        list.add(new Option("A", q.getOptionA()));
        list.add(new Option("B", q.getOptionB()));
        if (q.getOptionC() != null && !q.getOptionC().isBlank()) list.add(new Option("C", q.getOptionC()));
        if (q.getOptionD() != null && !q.getOptionD().isBlank()) list.add(new Option("D", q.getOptionD()));
        return list;
    }

    // ======================= Admin =======================

    @Transactional(readOnly = true)
    public List<QuizSummary> adminList() {
        return quizRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(q -> summary(q, q.getQuestions().size(), null, null))
                .toList();
    }

    @Transactional(readOnly = true)
    public AdminQuiz adminGet(Long id) {
        return adminView(requireQuiz(id));
    }

    @Transactional
    public AdminQuiz create(QuizRequest req) {
        Quiz quiz = new Quiz();
        apply(quiz, req);
        return adminView(quizRepository.save(quiz));
    }

    @Transactional
    public AdminQuiz update(Long id, QuizRequest req) {
        Quiz quiz = requireQuiz(id);
        apply(quiz, req);
        return adminView(quizRepository.save(quiz));
    }

    @Transactional
    public void delete(Long id) {
        Quiz quiz = requireQuiz(id);
        attemptRepository.deleteByQuizId(id);
        quizRepository.delete(quiz);
    }

    private void apply(Quiz quiz, QuizRequest req) {
        quiz.setTitle(req.title().trim());
        quiz.setDescription(CourseService.blankToNull(req.description()));
        quiz.setCategory(CourseService.blankToNull(req.category()));
        quiz.setCourse(req.courseId() == null ? null : courseService.requireCourse(req.courseId()));
        quiz.setPassPercentage(req.passPercentage() == null ? 60 : req.passPercentage());
        quiz.setMaxAttempts(req.maxAttempts() == null ? 3 : req.maxAttempts());
        if (req.published() != null) {
            quiz.setPublished(req.published());
        }

        // Reuse existing questions by id so students in the middle of a quiz can still submit.
        Map<Long, Question> existing = new HashMap<>();
        for (Question q : quiz.getQuestions()) {
            if (q.getId() != null) existing.put(q.getId(), q);
        }
        List<Question> newQuestions = new ArrayList<>();
        for (int i = 0; i < req.questions().size(); i++) {
            QuestionRequest r = req.questions().get(i);
            String correct = r.correctOption().trim().toUpperCase(Locale.ROOT);
            String chosen = switch (correct) {
                case "A" -> r.optionA();
                case "B" -> r.optionB();
                case "C" -> r.optionC();
                default -> r.optionD();
            };
            if (chosen == null || chosen.isBlank()) {
                throw ApiException.badRequest("Question " + (i + 1) + ": the correct answer (" + correct + ") points to an empty option");
            }
            Question q = r.id() != null ? existing.remove(r.id()) : null;
            if (q == null) {
                q = new Question();
            }
            q.setQuiz(quiz);
            q.setQuestionText(r.questionText().trim());
            q.setOptionA(r.optionA().trim());
            q.setOptionB(r.optionB().trim());
            q.setOptionC(CourseService.blankToNull(r.optionC()));
            q.setOptionD(CourseService.blankToNull(r.optionD()));
            q.setCorrectOption(correct);
            q.setPosition(i);
            newQuestions.add(q);
        }
        quiz.getQuestions().clear();
        quiz.getQuestions().addAll(newQuestions);
    }

    private AdminQuiz adminView(Quiz q) {
        List<AdminQuestion> questions = q.getQuestions().stream()
                .map(x -> new AdminQuestion(x.getId(), x.getQuestionText(), x.getOptionA(), x.getOptionB(),
                        x.getOptionC(), x.getOptionD(), x.getCorrectOption()))
                .toList();
        return new AdminQuiz(summary(q, questions.size(), null, null), questions);
    }

    private Quiz requireQuiz(Long id) {
        return quizRepository.findById(id).orElseThrow(() -> ApiException.notFound("Quiz"));
    }
}
