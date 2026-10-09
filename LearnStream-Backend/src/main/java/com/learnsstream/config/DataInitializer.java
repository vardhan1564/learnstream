package com.learnsstream.config;

import com.learnsstream.entity.*;
import com.learnsstream.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * Runs once on startup:
 *  1. Creates the first admin from learnstream.admin.email / password (if no admin exists yet).
 *  2. Seeds sample content when the database is empty (learnstream.seed-demo-data=true),
 *     so you can try every feature straight away. Edit or delete it from the admin panel.
 */
@Component
@Order(1)
public class DataInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    private final UserRepository userRepository;
    private final CourseRepository courseRepository;
    private final ProblemRepository problemRepository;
    private final QuizRepository quizRepository;
    private final RoadmapRepository roadmapRepository;
    private final PasswordEncoder passwordEncoder;

    @Value("${learnstream.admin.email:}")
    private String adminEmail;
    @Value("${learnstream.admin.password:}")
    private String adminPassword;
    @Value("${learnstream.admin.name:Platform Admin}")
    private String adminName;
    @Value("${learnstream.seed-demo-data:true}")
    private boolean seedDemoData;

    public DataInitializer(UserRepository userRepository, CourseRepository courseRepository,
                           ProblemRepository problemRepository, QuizRepository quizRepository,
                           RoadmapRepository roadmapRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.courseRepository = courseRepository;
        this.problemRepository = problemRepository;
        this.quizRepository = quizRepository;
        this.roadmapRepository = roadmapRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    @Transactional
    public void run(String... args) {
        createAdmin();
        if (seedDemoData && courseRepository.count() == 0 && problemRepository.count() == 0
                && quizRepository.count() == 0 && roadmapRepository.count() == 0) {
            seed();
        }
    }

    private void createAdmin() {
        if (userRepository.existsByRole(Role.ADMIN)) {
            return;
        }
        if (adminEmail == null || adminEmail.isBlank() || adminPassword == null || adminPassword.isBlank()) {
            log.warn("No admin account exists. Set learnstream.admin.email and learnstream.admin.password "
                    + "(or ADMIN_EMAIL / ADMIN_PASSWORD) and restart to create one.");
            return;
        }
        String email = adminEmail.trim().toLowerCase(Locale.ROOT);
        User admin = userRepository.findByEmailIgnoreCase(email).orElseGet(User::new);
        admin.setEmail(email);
        admin.setFullName(adminName);
        admin.setPassword(passwordEncoder.encode(adminPassword));
        admin.setRole(Role.ADMIN);
        admin.setVerified(true);
        userRepository.save(admin);
        log.info("Admin account ready: {}", email);
    }

    // ------------------------------------------------------------------ demo content

    private void seed() {
        log.info("Seeding demo content (courses, problems, quizzes, roadmaps)...");

        Course java = course("Java Programming for Beginners",
                "Start your coding journey with Java. Learn variables, control flow, methods and object-oriented "
                + "programming, then prove your skills in the course quiz to earn a certificate.",
                0.0, "Java", "Beginner");
        lesson(java, "Java Tutorial for Beginners", "https://www.youtube.com/watch?v=eIrMbAQSU34", 150, true);
        courseRepository.save(java);

        Course dsa = course("Data Structures & Algorithms",
                "Master the data structures and algorithms asked in technical interviews: arrays, linked lists, "
                + "trees, graphs, sorting, searching and Big-O analysis.",
                499.0, "DSA", "Intermediate");
        lesson(dsa, "Algorithms and Data Structures - Introduction", "https://www.youtube.com/watch?v=8hly31xKli0", 300, true);
        lesson(dsa, "Data Structures: Easy to Advanced", "https://www.youtube.com/watch?v=RBSGKlAvoiM", 480, false);
        courseRepository.save(dsa);

        Course python = course("Python for Everyone",
                "A complete beginner-friendly Python course: syntax, data types, functions, files and small projects.",
                299.0, "Python", "Beginner");
        lesson(python, "Learn Python - Full Course for Beginners", "https://www.youtube.com/watch?v=rfscVS0vtbw", 270, true);
        courseRepository.save(python);

        Course js = course("JavaScript Essentials",
                "Learn modern JavaScript from scratch - the language of the web.",
                399.0, "Web Development", "Beginner");
        lesson(js, "Learn JavaScript - Full Course for Beginners", "https://www.youtube.com/watch?v=PkZNo7MFNFg", 205, true);
        courseRepository.save(js);

        quiz("Java Basics Assessment", "Pass this quiz (60%+) to unlock your Java course certificate.", "Java", java, List.of(
                q("Which keyword is used to inherit a class in Java?", "implements", "extends", "inherits", "super", "B"),
                q("What is the default value of an int field in a Java class?", "0", "null", "1", "undefined", "A"),
                q("Which of these is NOT a primitive type in Java?", "int", "boolean", "String", "char", "C"),
                q("What does JVM stand for?", "Java Variable Machine", "Java Virtual Machine", "Joint Virtual Method", "Java Verified Mode", "B"),
                q("Which method is the entry point of a Java program?", "start()", "run()", "main()", "init()", "C")));

        quiz("DSA Fundamentals", "Quick check of core data-structure and complexity concepts.", "DSA", null, List.of(
                q("What is the time complexity of binary search on a sorted array?", "O(n)", "O(log n)", "O(n log n)", "O(1)", "B"),
                q("Which data structure follows LIFO (Last In, First Out)?", "Queue", "Stack", "Heap", "Graph", "B"),
                q("What is the worst-case time complexity of quicksort?", "O(n log n)", "O(n)", "O(n^2)", "O(log n)", "C"),
                q("Which data structure is used for breadth-first search (BFS)?", "Stack", "Queue", "Tree", "Array", "B"),
                q("Average time complexity of a hash map lookup?", "O(1)", "O(n)", "O(log n)", "O(n^2)", "A")));

        seedProblems();

        Roadmap backend = roadmap("Java Backend Developer",
                "From zero to building production-ready REST APIs with Java and Spring Boot.", "Beginner", "4-6 months");
        step(backend, "Java fundamentals", "Syntax, variables, loops, methods and OOP basics.", null, java);
        step(backend, "OOP, Collections & Exceptions", "Classes, interfaces, generics, List/Map/Set and error handling.", "https://dev.java/learn/", null);
        step(backend, "Data Structures & Algorithms", "Arrays, hashing, recursion, trees and graphs. Solve problems daily.", null, dsa);
        step(backend, "SQL & relational databases", "Tables, joins, indexes and transactions with MySQL.", "https://www.w3schools.com/sql/", null);
        step(backend, "Spring Boot & REST APIs", "Controllers, services, JPA, validation and security with JWT.", "https://spring.io/guides", null);
        step(backend, "Build and deploy a project", "Ship a full project (like LearnStream!) and put it on GitHub.", "https://docs.github.com/en/get-started", null);
        roadmapRepository.save(backend);

        Roadmap interview = roadmap("DSA for Coding Interviews",
                "A focused path through the topics that appear most often in coding interviews.", "Intermediate", "8-10 weeks");
        step(interview, "Arrays & Strings", "Two pointers, sliding window and prefix sums.", null, null);
        step(interview, "Hashing", "HashMap / HashSet patterns for O(1) lookups.", null, null);
        step(interview, "Recursion & Backtracking", "Think in sub-problems; permutations and subsets.", null, null);
        step(interview, "Trees & Graphs", "DFS, BFS, binary search trees and shortest paths.", null, dsa);
        step(interview, "Dynamic Programming", "Memoization and tabulation for classic problems.", "https://www.geeksforgeeks.org/dynamic-programming/", null);
        roadmapRepository.save(interview);

        log.info("Demo content ready.");
    }

    private void seedProblems() {
        problem("Sum of Two Numbers", "EASY", "Basics,Math",
                "Read two integers a and b and print their sum.",
                "A single line with two integers a and b separated by a space.",
                "Print a single integer: a + b.",
                "-2 x 10^9 <= a, b <= 2 x 10^9 (the sum may not fit in a 32-bit int!)",
                List.of(tc("2 3", "5", true), tc("-4 10", "6", true), tc("0 0", "0", false),
                        tc("2000000000 1500000000", "3500000000", false), tc("-7 -8", "-15", false)));

        problem("Reverse a String", "EASY", "Strings",
                "Given a string s, print it reversed.",
                "A single line containing the string s (no spaces).",
                "Print the reversed string.",
                "1 <= length of s <= 10^5",
                List.of(tc("hello", "olleh", true), tc("LearnStream", "maertSnraeL", true), tc("a", "a", false),
                        tc("racecar", "racecar", false), tc("12345", "54321", false)));

        problem("Find the Maximum", "EASY", "Arrays",
                "Given n integers, print the largest one.",
                "The first line contains n. The second line contains n integers separated by spaces.",
                "Print the maximum value.",
                "1 <= n <= 10^5, -10^9 <= value <= 10^9",
                List.of(tc("5\n3 9 2 7 4", "9", true), tc("3\n-5 -1 -9", "-1", true), tc("1\n42", "42", false),
                        tc("6\n100 200 300 300 50 0", "300", false)));

        problem("Palindrome Check", "EASY", "Strings,Two Pointers",
                "A palindrome reads the same forwards and backwards. Given a string s, print YES if it is a palindrome, otherwise NO. The check is case-sensitive.",
                "A single line containing the string s (no spaces).",
                "Print YES or NO.",
                "1 <= length of s <= 10^5",
                List.of(tc("madam", "YES", true), tc("hello", "NO", true), tc("a", "YES", false),
                        tc("abba", "YES", false), tc("abca", "NO", false), tc("Aa", "NO", false)));

        problem("FizzBuzz", "EASY", "Basics,Loops",
                "Print the numbers from 1 to n, one per line. But for multiples of 3 print Fizz, for multiples of 5 print Buzz, and for multiples of both print FizzBuzz.",
                "A single integer n.",
                "n lines as described.",
                "1 <= n <= 1000",
                List.of(tc("5", fizz(5), true), tc("15", fizz(15), true), tc("1", fizz(1), false), tc("30", fizz(30), false)));

        problem("Two Sum", "MEDIUM", "Arrays,Hashing",
                "Given an array of n integers and a target, find the two different indices i < j such that nums[i] + nums[j] = target. Exactly one answer exists. Indices are 0-based.",
                "Line 1: n. Line 2: n integers. Line 3: target.",
                "Print i and j separated by a space.",
                "2 <= n <= 10^5. Try to beat O(n^2)!",
                List.of(tc("4\n2 7 11 15\n9", "0 1", true), tc("3\n3 2 4\n6", "1 2", true), tc("2\n3 3\n6", "0 1", false),
                        tc("5\n1 5 3 8 2\n10", "3 4", false)));

        problem("Longest Substring Without Repeating Characters", "MEDIUM", "Strings,Sliding Window",
                "Given a string s, print the length of the longest substring that contains no repeated characters.",
                "A single line containing s (lowercase letters only).",
                "Print one integer.",
                "1 <= length of s <= 10^5",
                List.of(tc("abcabcbb", "3", true), tc("bbbbb", "1", true), tc("pwwkew", "3", false),
                        tc("dvdf", "3", false), tc("a", "1", false), tc("abcdefg", "7", false)));

        String bigInput = "5000\n" + IntStream.rangeClosed(1, 5000).map(i -> 5001 - i)
                .mapToObj(String::valueOf).collect(Collectors.joining(" "));
        problem("Count Inversions", "HARD", "Arrays,Divide and Conquer,Merge Sort",
                "An inversion is a pair of indices (i, j) with i < j and a[i] > a[j]. Count the inversions in the array.",
                "Line 1: n. Line 2: n integers.",
                "Print the number of inversions (it can exceed the 32-bit range).",
                "1 <= n <= 10^5. An O(n log n) merge-sort solution is expected.",
                List.of(tc("5\n2 4 1 3 5", "3", true), tc("3\n3 2 1", "3", true), tc("4\n1 2 3 4", "0", false),
                        tc(bigInput, "12497500", false)));
    }

    // ------------------------------------------------------------------ builders

    private Course course(String title, String description, double price, String category, String level) {
        Course c = new Course();
        c.setTitle(title);
        c.setDescription(description);
        c.setPrice(price);
        c.setCategory(category);
        c.setLevel(level);
        c.setInstructor("LearnStream Team");
        c.setPublished(true);
        return c;
    }

    private void lesson(Course c, String title, String url, int minutes, boolean preview) {
        Lesson l = new Lesson();
        l.setTitle(title);
        l.setVideoUrl(url);
        l.setDurationMinutes(minutes);
        l.setPreview(preview);
        l.setPosition(c.getLessons().size());
        l.setCourse(c);
        c.getLessons().add(l);
    }

    private record QuestionSeed(String text, String a, String b, String c, String d, String correct) {}

    private static QuestionSeed q(String text, String a, String b, String c, String d, String correct) {
        return new QuestionSeed(text, a, b, c, d, correct);
    }

    private void quiz(String title, String description, String category, Course course, List<QuestionSeed> questions) {
        Quiz quiz = new Quiz();
        quiz.setTitle(title);
        quiz.setDescription(description);
        quiz.setCategory(category);
        quiz.setCourse(course);
        quiz.setPassPercentage(60);
        quiz.setMaxAttempts(3);
        for (int i = 0; i < questions.size(); i++) {
            QuestionSeed s = questions.get(i);
            Question qn = new Question();
            qn.setQuiz(quiz);
            qn.setQuestionText(s.text());
            qn.setOptionA(s.a());
            qn.setOptionB(s.b());
            qn.setOptionC(s.c());
            qn.setOptionD(s.d());
            qn.setCorrectOption(s.correct());
            qn.setPosition(i);
            quiz.getQuestions().add(qn);
        }
        quizRepository.save(quiz);
    }

    private record TestSeed(String input, String expected, boolean sample) {}

    private static TestSeed tc(String input, String expected, boolean sample) {
        return new TestSeed(input, expected, sample);
    }

    private void problem(String title, String difficulty, String tags, String description, String inputFormat,
                         String outputFormat, String constraints, List<TestSeed> tests) {
        Problem p = new Problem();
        p.setTitle(title);
        p.setDifficulty(difficulty);
        p.setTags(tags);
        p.setDescription(description);
        p.setInputFormat(inputFormat);
        p.setOutputFormat(outputFormat);
        p.setConstraintsText(constraints);
        for (int i = 0; i < tests.size(); i++) {
            TestSeed s = tests.get(i);
            TestCase t = new TestCase();
            t.setProblem(p);
            t.setInput(s.input());
            t.setExpectedOutput(s.expected());
            t.setSample(s.sample());
            t.setPosition(i);
            p.getTestCases().add(t);
        }
        problemRepository.save(p);
    }

    private Roadmap roadmap(String title, String description, String level, String duration) {
        Roadmap r = new Roadmap();
        r.setTitle(title);
        r.setDescription(description);
        r.setLevel(level);
        r.setDuration(duration);
        return r;
    }

    private void step(Roadmap r, String title, String description, String url, Course course) {
        RoadmapStep s = new RoadmapStep();
        s.setRoadmap(r);
        s.setTitle(title);
        s.setDescription(description);
        s.setResourceUrl(url);
        s.setCourse(course);
        s.setPosition(r.getSteps().size());
        r.getSteps().add(s);
    }

    private static String fizz(int n) {
        return IntStream.rangeClosed(1, n)
                .mapToObj(i -> i % 15 == 0 ? "FizzBuzz" : i % 3 == 0 ? "Fizz" : i % 5 == 0 ? "Buzz" : String.valueOf(i))
                .collect(Collectors.joining("\n"));
    }
}
