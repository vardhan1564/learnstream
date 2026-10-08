package com.learnsstream.service;

import com.learnsstream.dto.ProblemDtos.*;
import com.learnsstream.entity.Problem;
import com.learnsstream.entity.Submission;
import com.learnsstream.entity.TestCase;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.ProblemRepository;
import com.learnsstream.repository.SubmissionRepository;
import com.learnsstream.repository.UserRepository;
import com.learnsstream.security.AuthUser;
import com.learnsstream.security.RateLimiter;
import com.learnsstream.service.CodeExecutionService.ExecResult;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.*;
import java.util.regex.Pattern;

@Service
public class ProblemService {

    private static final Pattern JAVA_MAIN = Pattern.compile("\\bclass\\s+Main\\b");

    public static final Map<String, String> DEFAULT_STARTERS = Map.of(
            "java", """
                    import java.util.*;

                    public class Main {
                        public static void main(String[] args) {
                            Scanner sc = new Scanner(System.in);
                            // Read the input, solve the problem and print the answer
                        }
                    }
                    """,
            "python", """
                    import sys

                    def main():
                        data = sys.stdin.read().split()
                        # Solve the problem and print the answer

                    if __name__ == "__main__":
                        main()
                    """,
            "cpp", """
                    #include <bits/stdc++.h>
                    using namespace std;

                    int main() {
                        ios::sync_with_stdio(false);
                        cin.tie(nullptr);
                        // Read the input, solve the problem and print the answer
                        return 0;
                    }
                    """,
            "javascript", """
                    const input = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/);
                    // Solve the problem and print the answer with console.log()
                    """);

    /** Snapshot of the data needed to run code, so no DB transaction is held during the (slow) Judge0 call. */
    private record ProblemSnapshot(Long id, List<TestCaseData> tests) {}

    private record TestCaseData(String input, String expected, boolean sample) {}

    private final ProblemRepository problemRepository;
    private final SubmissionRepository submissionRepository;
    private final UserRepository userRepository;
    private final CodeExecutionService executor;
    private final RewardService rewardService;
    private final RateLimiter rateLimiter;
    private final TransactionTemplate tx;

    public ProblemService(ProblemRepository problemRepository, SubmissionRepository submissionRepository,
                          UserRepository userRepository, CodeExecutionService executor, RewardService rewardService,
                          RateLimiter rateLimiter, PlatformTransactionManager transactionManager) {
        this.problemRepository = problemRepository;
        this.submissionRepository = submissionRepository;
        this.userRepository = userRepository;
        this.executor = executor;
        this.rewardService = rewardService;
        this.rateLimiter = rateLimiter;
        this.tx = new TransactionTemplate(transactionManager);
    }

    // ======================= Student =======================

    public List<LanguageInfo> languages() {
        return CodeExecutionService.LANGUAGE_NAMES.entrySet().stream()
                .map(e -> new LanguageInfo(e.getKey(), e.getValue()))
                .toList();
    }

    @Transactional(readOnly = true)
    public List<ProblemSummary> list(AuthUser viewer) {
        Set<Long> solved = viewer == null ? Set.of() : new HashSet<>(submissionRepository.findSolvedProblemIds(viewer.id()));
        return problemRepository.findByPublishedTrueOrderByIdAsc().stream()
                .map(p -> new ProblemSummary(p.getId(), p.getTitle(), p.getDifficulty(), p.getTags(), true, solved.contains(p.getId())))
                .toList();
    }

    @Transactional(readOnly = true)
    public ProblemDetail detail(Long id, AuthUser viewer) {
        Problem p = accessibleProblem(id, viewer);
        List<SampleTest> samples = p.getTestCases().stream()
                .filter(TestCase::isSample)
                .map(t -> new SampleTest(t.getInput(), t.getExpectedOutput()))
                .toList();
        int hidden = (int) p.getTestCases().stream().filter(t -> !t.isSample()).count();
        boolean solved = viewer != null
                && submissionRepository.existsByUserIdAndProblemIdAndStatus(viewer.id(), id, Submission.ACCEPTED);
        return new ProblemDetail(p.getId(), p.getTitle(), p.getDescription(), p.getDifficulty(),
                p.getInputFormat(), p.getOutputFormat(), p.getConstraintsText(), p.getTags(),
                starters(p), samples, hidden, solved);
    }

    /** "Run": sample tests only (or the student's custom input). Nothing is saved. */
    public RunResponse run(Long id, RunRequest req, AuthUser viewer) {
        validate(req);
        rateLimiter.check("run:" + viewer.id(), 1, 2, "Please wait a moment before running again.");
        rateLimiter.check("run-min:" + viewer.id(), 20, 60, "Too many runs in a minute. Take a short break and try again.");
        ProblemSnapshot snap = snapshot(id, viewer);

        if (req.customInput() != null) {
            ExecResult r = executor.runAll(req.language(), req.code(), List.of(req.customInput())).get(0);
            String verdict = verdict(r, null);
            boolean ok = !"COMPILATION_ERROR".equals(verdict) && !"RUNTIME_ERROR".equals(verdict)
                    && !"TIME_LIMIT_EXCEEDED".equals(verdict) && !"ERROR".equals(verdict);
            TestResult tr = new TestResult(1, false, ok, ok ? "EXECUTED" : verdict, req.customInput(), null,
                    clip(r.stdout()), r.time(), r.memory());
            return new RunResponse(ok ? "EXECUTED" : verdict, ok ? 1 : 0, 1, clip(r.compileOutput()),
                    clip(errorText(r)), List.of(tr), false, false, null);
        }

        List<TestCaseData> tests = snap.tests().stream().filter(TestCaseData::sample).toList();
        if (tests.isEmpty() && !snap.tests().isEmpty()) {
            tests = List.of(snap.tests().get(0)); // no sample marked: use the first test, still hidden
        }
        return execute(req, tests);
    }

    /** "Submit": every test case (including hidden ones). Saved to history; first accept counts towards rewards. */
    public RunResponse submit(Long id, RunRequest req, AuthUser viewer) {
        validate(req);
        rateLimiter.check("submit:" + viewer.id(), 1, 4, "Please wait a few seconds before submitting again.");
        rateLimiter.check("submit-min:" + viewer.id(), 10, 60, "Too many submissions in a minute. Take a short break.");
        ProblemSnapshot snap = snapshot(id, viewer);
        if (snap.tests().isEmpty()) {
            throw ApiException.badRequest("This problem has no test cases yet");
        }

        RunResponse result = execute(req, snap.tests());
        boolean accepted = "ACCEPTED".equals(result.status());

        Boolean firstSolve = tx.execute(status -> {
            boolean alreadySolved = submissionRepository.existsByUserIdAndProblemIdAndStatus(viewer.id(), id, Submission.ACCEPTED);
            Submission s = new Submission();
            s.setUser(userRepository.getReferenceById(viewer.id()));
            s.setProblem(problemRepository.getReferenceById(id));
            s.setLanguage(req.language());
            s.setCode(req.code());
            s.setStatus(result.status());
            s.setPassedCount(result.passedCount());
            s.setTotalCount(result.totalCount());
            submissionRepository.save(s);
            return accepted && !alreadySolved;
        });

        return new RunResponse(result.status(), result.passedCount(), result.totalCount(), result.compileOutput(),
                result.stderr(), result.results(), accepted, Boolean.TRUE.equals(firstSolve),
                rewardService.statusFor(viewer.id()));
    }

    @Transactional(readOnly = true)
    public List<SubmissionView> history(Long problemId, AuthUser viewer) {
        return submissionRepository.findHistory(viewer.id(), problemId, PageRequest.of(0, 20)).stream()
                .map(s -> new SubmissionView(s.getId(), s.getLanguage(), s.getStatus(), s.getPassedCount(),
                        s.getTotalCount(), s.getSubmittedAt(), s.getCode()))
                .toList();
    }

    private RunResponse execute(RunRequest req, List<TestCaseData> tests) {
        List<String> inputs = tests.stream().map(TestCaseData::input).toList();
        List<ExecResult> results = executor.runAll(req.language(), req.code(), inputs);

        List<TestResult> out = new ArrayList<>();
        int passed = 0;
        String overall = "ACCEPTED";
        String compileOutput = "";
        String stderr = "";
        for (int i = 0; i < tests.size(); i++) {
            TestCaseData t = tests.get(i);
            ExecResult r = results.get(i);
            String verdict = verdict(r, t.expected());
            boolean ok = "ACCEPTED".equals(verdict);
            if (ok) {
                passed++;
            } else if ("ACCEPTED".equals(overall)) {
                overall = verdict; // first failure decides the overall verdict
                compileOutput = clip(r.compileOutput()); // compile errors happen before any input is read
                // Never echo stderr of a hidden test: a program could print the hidden input there.
                stderr = t.sample() ? clip(errorText(r)) : "";
            }
            boolean hidden = !t.sample();
            out.add(new TestResult(i + 1, hidden, ok, verdict,
                    hidden ? null : t.input(),
                    hidden ? null : t.expected(),
                    hidden ? null : clip(r.stdout()),
                    r.time(), r.memory()));
            if ("COMPILATION_ERROR".equals(verdict)) {
                // Same compile error for every test - no need to show it N times
                for (int j = i + 1; j < tests.size(); j++) {
                    out.add(new TestResult(j + 1, !tests.get(j).sample(), false, verdict, null, null, null, null, null));
                }
                break;
            }
        }
        return new RunResponse(overall, passed, tests.size(), compileOutput, stderr, out, false, false, null);
    }

    /** Maps a Judge0 status to our verdict, comparing output ourselves (ignores trailing spaces / blank lines). */
    private static String verdict(ExecResult r, String expected) {
        int id = r.statusId();
        if (id == 3 || id == 4) {
            if (expected == null) return "ACCEPTED";
            return normalize(r.stdout()).equals(normalize(expected)) ? "ACCEPTED" : "WRONG_ANSWER";
        }
        if (id == 5) return "TIME_LIMIT_EXCEEDED";
        if (id == 6) return "COMPILATION_ERROR";
        if (id >= 7 && id <= 12) return "RUNTIME_ERROR";
        return "ERROR";
    }

    static String normalize(String s) {
        if (s == null) return "";
        String[] lines = s.replace("\r\n", "\n").replace('\r', '\n').split("\n", -1);
        StringBuilder sb = new StringBuilder();
        for (String line : lines) {
            sb.append(line.stripTrailing()).append('\n');
        }
        return sb.toString().strip();
    }

    private static String errorText(ExecResult r) {
        String err = r.stderr() == null ? "" : r.stderr();
        if (err.isBlank() && r.message() != null && !r.message().isBlank() && r.statusId() != 3) {
            err = r.message();
        }
        return err;
    }

    private static String clip(String s) {
        if (s == null) return "";
        return s.length() > 5000 ? s.substring(0, 5000) + "\n... (output truncated)" : s;
    }

    private void validate(RunRequest req) {
        if (!executor.isSupported(req.language())) {
            throw ApiException.badRequest("Unsupported language. Choose one of: " + String.join(", ", CodeExecutionService.LANGUAGE_NAMES.keySet()));
        }
        if ("java".equals(req.language()) && !JAVA_MAIN.matcher(req.code()).find()) {
            throw ApiException.badRequest("Java code must have a class named Main (public class Main { ... })");
        }
    }

    private ProblemSnapshot snapshot(Long id, AuthUser viewer) {
        return tx.execute(status -> {
            Problem p = accessibleProblem(id, viewer);
            List<TestCaseData> tests = p.getTestCases().stream()
                    .map(t -> new TestCaseData(t.getInput() == null ? "" : t.getInput(), t.getExpectedOutput(), t.isSample()))
                    .toList();
            return new ProblemSnapshot(p.getId(), tests);
        });
    }

    private Problem accessibleProblem(Long id, AuthUser viewer) {
        Problem p = problemRepository.findById(id).orElseThrow(() -> ApiException.notFound("Problem"));
        if (!p.isPublished() && (viewer == null || !viewer.isAdmin())) {
            throw ApiException.notFound("Problem");
        }
        return p;
    }

    private static Map<String, String> starters(Problem p) {
        Map<String, String> m = new LinkedHashMap<>();
        m.put("java", orDefault(p.getStarterJava(), "java"));
        m.put("python", orDefault(p.getStarterPython(), "python"));
        m.put("cpp", orDefault(p.getStarterCpp(), "cpp"));
        m.put("javascript", orDefault(p.getStarterJavascript(), "javascript"));
        return m;
    }

    private static String orDefault(String value, String lang) {
        return value == null || value.isBlank() ? DEFAULT_STARTERS.get(lang) : value;
    }

    // ======================= Admin =======================

    @Transactional(readOnly = true)
    public List<AdminProblem> adminList() {
        return problemRepository.findAllByOrderByIdDesc().stream().map(this::adminView).toList();
    }

    @Transactional(readOnly = true)
    public AdminProblem adminGet(Long id) {
        return adminView(problemRepository.findById(id).orElseThrow(() -> ApiException.notFound("Problem")));
    }

    @Transactional
    public AdminProblem create(ProblemRequest req) {
        Problem p = new Problem();
        apply(p, req);
        return adminView(problemRepository.save(p));
    }

    @Transactional
    public AdminProblem update(Long id, ProblemRequest req) {
        Problem p = problemRepository.findById(id).orElseThrow(() -> ApiException.notFound("Problem"));
        apply(p, req);
        return adminView(problemRepository.save(p));
    }

    @Transactional
    public void delete(Long id) {
        Problem p = problemRepository.findById(id).orElseThrow(() -> ApiException.notFound("Problem"));
        submissionRepository.deleteByProblemId(id);
        problemRepository.delete(p);
    }

    private void apply(Problem p, ProblemRequest req) {
        p.setTitle(req.title().trim());
        p.setDescription(req.description().trim());
        p.setDifficulty(req.difficulty());
        p.setInputFormat(CourseService.blankToNull(req.inputFormat()));
        p.setOutputFormat(CourseService.blankToNull(req.outputFormat()));
        p.setConstraintsText(CourseService.blankToNull(req.constraintsText()));
        p.setTags(CourseService.blankToNull(req.tags()));
        p.setStarterJava(blankToNullKeepIndent(req.starterJava()));
        p.setStarterPython(blankToNullKeepIndent(req.starterPython()));
        p.setStarterCpp(blankToNullKeepIndent(req.starterCpp()));
        p.setStarterJavascript(blankToNullKeepIndent(req.starterJavascript()));
        if (req.published() != null) {
            p.setPublished(req.published());
        }
        if (p.getStarterJava() != null && !JAVA_MAIN.matcher(p.getStarterJava()).find()) {
            throw ApiException.badRequest("Java starter code must contain 'public class Main' (required by the code runner)");
        }
        if (req.testCases().stream().noneMatch(t -> Boolean.TRUE.equals(t.sample()))) {
            throw ApiException.badRequest("Mark at least one test case as a sample so students can see an example");
        }
        List<TestCase> tests = new ArrayList<>();
        for (int i = 0; i < req.testCases().size(); i++) {
            var r = req.testCases().get(i);
            TestCase t = new TestCase();
            t.setProblem(p);
            t.setInput(r.input() == null ? "" : r.input());
            t.setExpectedOutput(r.expectedOutput());
            t.setSample(Boolean.TRUE.equals(r.sample()));
            t.setPosition(i);
            tests.add(t);
        }
        p.getTestCases().clear();
        p.getTestCases().addAll(tests);
    }

    private static String blankToNullKeepIndent(String s) {
        return (s == null || s.isBlank()) ? null : s.stripTrailing() + "\n";
    }

    private AdminProblem adminView(Problem p) {
        List<AdminTestCase> tests = p.getTestCases().stream()
                .map(t -> new AdminTestCase(t.getId(), t.getInput(), t.getExpectedOutput(), t.isSample()))
                .toList();
        return new AdminProblem(p.getId(), p.getTitle(), p.getDescription(), p.getDifficulty(),
                p.getInputFormat(), p.getOutputFormat(), p.getConstraintsText(), p.getTags(),
                p.getStarterJava(), p.getStarterPython(), p.getStarterCpp(), p.getStarterJavascript(),
                p.isPublished(), tests, p.getCreatedAt());
    }
}
