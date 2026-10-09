package com.learnsstream.config;

import com.learnsstream.entity.Problem;
import com.learnsstream.entity.Question;
import com.learnsstream.entity.Quiz;
import com.learnsstream.entity.TestCase;
import com.learnsstream.repository.ProblemRepository;
import com.learnsstream.repository.QuizRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import tools.jackson.databind.MappingIterator;
import tools.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;

/**
 * Adds the bundled practice content (seed/problems.json and seed/quizzes.json, built from seed-src/)
 * on every startup. Items are matched by title, so only new ones are inserted and anything already
 * in the database (including admin edits) is left alone. Disable with SEED_CONTENT=false - e.g. if you
 * delete a bundled problem and don't want it to come back on the next restart.
 */
@Component
@Order(2)
public class ContentSeeder implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(ContentSeeder.class);

    record TestSeed(String input, String expected, boolean sample) {}

    record ProblemSeed(String title, String difficulty, String tags, String description, String input_format,
                       String output_format, String constraints, List<TestSeed> tests) {}

    record QuestionSeed(String q, List<String> options, String answer) {}

    record QuizSeed(String title, String description, String category, List<QuestionSeed> questions) {}

    private final ProblemRepository problemRepository;
    private final QuizRepository quizRepository;
    private final ObjectMapper objectMapper;

    @Value("${learnstream.seed-content:true}")
    private boolean enabled;

    public ContentSeeder(ProblemRepository problemRepository, QuizRepository quizRepository, ObjectMapper objectMapper) {
        this.problemRepository = problemRepository;
        this.quizRepository = quizRepository;
        this.objectMapper = objectMapper;
    }

    @Override
    public void run(String... args) {
        if (!enabled) {
            return;
        }
        try {
            int problems = seedProblems();
            int quizzes = seedQuizzes();
            if (problems + quizzes > 0) {
                log.info("Content pack: added {} problems and {} quizzes", problems, quizzes);
            }
        } catch (RuntimeException | IOException e) {
            // Never stop the app from starting because of seed content.
            log.error("Could not load the content pack", e);
        }
    }

    private int seedProblems() throws IOException {
        Set<String> existing = new HashSet<>(problemRepository.findAllTitles());
        int[] added = {0};
        // The pack is large (big hidden tests), so stream it one problem at a time.
        forEach("seed/problems.json", ProblemSeed.class, s -> {
            if (!existing.add(s.title())) {
                return;
            }
            Problem p = new Problem();
            p.setTitle(s.title());
            p.setDifficulty(s.difficulty());
            p.setTags(s.tags());
            p.setDescription(s.description());
            p.setInputFormat(s.input_format());
            p.setOutputFormat(s.output_format());
            p.setConstraintsText(s.constraints());
            for (int i = 0; i < s.tests().size(); i++) {
                TestSeed t = s.tests().get(i);
                TestCase tc = new TestCase();
                tc.setProblem(p);
                tc.setInput(t.input());
                tc.setExpectedOutput(t.expected());
                tc.setSample(t.sample());
                tc.setPosition(i);
                p.getTestCases().add(tc);
            }
            problemRepository.save(p);
            added[0]++;
        });
        return added[0];
    }

    private int seedQuizzes() throws IOException {
        Set<String> existing = new HashSet<>(quizRepository.findAllTitles());
        int[] added = {0};
        forEach("seed/quizzes.json", QuizSeed.class, s -> {
            if (!existing.add(s.title())) {
                return;
            }
            Quiz quiz = new Quiz();
            quiz.setTitle(s.title());
            quiz.setDescription(s.description());
            quiz.setCategory(s.category());
            quiz.setPassPercentage(60);
            quiz.setMaxAttempts(0); // practice quizzes: unlimited attempts
            for (int i = 0; i < s.questions().size(); i++) {
                QuestionSeed qs = s.questions().get(i);
                Question qn = new Question();
                qn.setQuiz(quiz);
                qn.setQuestionText(qs.q());
                qn.setOptionA(qs.options().get(0));
                qn.setOptionB(qs.options().get(1));
                qn.setOptionC(qs.options().get(2));
                qn.setOptionD(qs.options().get(3));
                qn.setCorrectOption(qs.answer());
                qn.setPosition(i);
                quiz.getQuestions().add(qn);
            }
            quizRepository.save(quiz);
            added[0]++;
        });
        return added[0];
    }

    /** Reads a JSON array element by element, so only one item is in memory at a time. */
    private <T> void forEach(String path, Class<T> type, Consumer<T> action) throws IOException {
        ClassPathResource resource = new ClassPathResource(path);
        if (!resource.exists()) {
            return;
        }
        try (InputStream in = resource.getInputStream();
             MappingIterator<T> items = objectMapper.readerFor(type).readValues(in)) {
            while (items.hasNext()) {
                action.accept(items.next());
            }
        }
    }
}
