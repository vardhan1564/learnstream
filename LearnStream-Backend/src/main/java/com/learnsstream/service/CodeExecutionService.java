package com.learnsstream.service;

import com.learnsstream.exception.ApiException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.BufferingClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.*;

/**
 * Runs code on Judge0 (https://judge0.com) using the batch API + polling, which works on the free
 * public instance, RapidAPI and self-hosted Judge0 alike. All text is base64 encoded so programs that
 * print non-UTF-8 bytes don't break the response (a common cause of "execution error" with Judge0).
 */
@Service
public class CodeExecutionService {

    private static final Logger log = LoggerFactory.getLogger(CodeExecutionService.class);
    private static final String FIELDS = "token,stdout,stderr,compile_output,message,status,time,memory";

    public record ExecResult(int statusId, String statusDescription, String stdout, String stderr,
                             String compileOutput, String message, String time, Integer memory) {}

    public static final Map<String, String> LANGUAGE_NAMES = new LinkedHashMap<>();

    static {
        LANGUAGE_NAMES.put("java", "Java");
        LANGUAGE_NAMES.put("python", "Python 3");
        LANGUAGE_NAMES.put("cpp", "C++");
        LANGUAGE_NAMES.put("javascript", "JavaScript (Node.js)");
    }

    @Value("${judge0.base-url:https://ce.judge0.com}")
    private String baseUrl;
    @Value("${judge0.api-key:}")
    private String apiKey;
    @Value("${judge0.api-host:}")
    private String apiHost;
    @Value("${judge0.auth-token:}")
    private String authToken;
    @Value("${judge0.language.java:62}")
    private int javaId;
    @Value("${judge0.language.python:71}")
    private int pythonId;
    @Value("${judge0.language.cpp:54}")
    private int cppId;
    @Value("${judge0.language.javascript:63}")
    private int javascriptId;
    @Value("${judge0.cpu-time-limit:5}")
    private double cpuTimeLimit;
    @Value("${judge0.timeout-seconds:30}")
    private int timeoutSeconds;

    private volatile RestClient client;

    public boolean isSupported(String language) {
        return language != null && LANGUAGE_NAMES.containsKey(language);
    }

    /** Runs the same program once per input, in parallel on Judge0. Results are in input order. */
    public List<ExecResult> runAll(String language, String code, List<String> inputs) {
        if (!isSupported(language)) {
            throw ApiException.badRequest("Unsupported language: " + language);
        }
        int languageId = switch (language) {
            case "java" -> javaId;
            case "python" -> pythonId;
            case "cpp" -> cppId;
            default -> javascriptId;
        };

        List<Map<String, Object>> submissions = new ArrayList<>();
        for (String input : inputs) {
            Map<String, Object> s = new HashMap<>();
            s.put("language_id", languageId);
            s.put("source_code", b64(code));
            s.put("stdin", b64(input == null ? "" : input));
            s.put("cpu_time_limit", cpuTimeLimit);
            submissions.add(s);
        }

        try {
            // Judge0 accepts at most 20 submissions per batch request by default.
            List<String> tokens = new ArrayList<>();
            for (int i = 0; i < submissions.size(); i += 20) {
                tokens.addAll(createBatch(submissions.subList(i, Math.min(i + 20, submissions.size()))));
            }
            List<ExecResult> results = new ArrayList<>();
            for (int i = 0; i < tokens.size(); i += 20) {
                results.addAll(pollBatch(tokens.subList(i, Math.min(i + 20, tokens.size()))));
            }
            return results;
        } catch (RestClientResponseException e) {
            int status = e.getStatusCode().value();
            log.warn("Judge0 returned {}: {}", status, e.getResponseBodyAsString());
            String msg = switch (status) {
                case 401, 403 -> "The code runner rejected our credentials. Ask the admin to check the Judge0 API key.";
                case 429 -> "The code runner is busy (rate limit reached). Please wait a few seconds and try again.";
                case 422 -> "The code runner could not accept this submission (check the language settings).";
                default -> "The code runner returned an error (" + status + "). Please try again.";
            };
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, msg);
        } catch (RestClientException e) {
            log.warn("Judge0 unreachable at {}: {}", baseUrl, e.getMessage());
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE,
                    "Could not reach the code runner. Please check your internet connection or try again later.");
        }
    }

    @SuppressWarnings("unchecked")
    private List<String> createBatch(List<Map<String, Object>> submissions) {
        List<Object> created = client().post()
                .uri("/submissions/batch?base64_encoded=true")
                .contentType(MediaType.APPLICATION_JSON)
                .body(Map.of("submissions", submissions))
                .retrieve()
                .body(List.class);
        if (created == null || created.size() != submissions.size()) {
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "The code runner returned an unexpected response.");
        }
        List<String> tokens = new ArrayList<>();
        for (Object o : created) {
            Map<String, Object> m = (Map<String, Object>) o;
            Object token = m.get("token");
            if (token == null) {
                throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "The code runner rejected the submission: " + m);
            }
            tokens.add(token.toString());
        }
        return tokens;
    }

    @SuppressWarnings("unchecked")
    private List<ExecResult> pollBatch(List<String> tokens) {
        long deadline = System.currentTimeMillis() + timeoutSeconds * 1000L;
        String joined = String.join(",", tokens);
        long sleep = 600;
        while (true) {
            Map<String, Object> body = client().get()
                    .uri("/submissions/batch?tokens={t}&base64_encoded=true&fields={f}", joined, FIELDS)
                    .retrieve()
                    .body(Map.class);
            List<Object> items = body == null ? List.of() : (List<Object>) body.getOrDefault("submissions", List.of());
            if (items.size() == tokens.size()) {
                List<ExecResult> results = new ArrayList<>();
                boolean done = true;
                for (Object item : items) {
                    ExecResult r = toResult((Map<String, Object>) item);
                    if (r.statusId() <= 2) { // 1 = In Queue, 2 = Processing
                        done = false;
                        break;
                    }
                    results.add(r);
                }
                if (done) {
                    return results;
                }
            }
            if (System.currentTimeMillis() > deadline) {
                throw new ApiException(HttpStatus.GATEWAY_TIMEOUT,
                        "The code runner is taking too long. Please try again in a moment.");
            }
            try {
                Thread.sleep(sleep);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "Execution was interrupted");
            }
            sleep = Math.min(sleep + 300, 2000);
        }
    }

    @SuppressWarnings("unchecked")
    private ExecResult toResult(Map<String, Object> m) {
        if (m == null) {
            return new ExecResult(13, "Internal Error", "", "", "", "No result", null, null);
        }
        Map<String, Object> status = (Map<String, Object>) m.get("status");
        int id = status == null || status.get("id") == null ? 13 : ((Number) status.get("id")).intValue();
        String desc = status == null || status.get("description") == null ? "Unknown" : status.get("description").toString();
        Integer memory = m.get("memory") instanceof Number n ? n.intValue() : null;
        String time = m.get("time") == null ? null : m.get("time").toString();
        return new ExecResult(id, desc, unb64(m.get("stdout")), unb64(m.get("stderr")),
                unb64(m.get("compile_output")), unb64(m.get("message")), time, memory);
    }

    private RestClient client() {
        RestClient c = client;
        if (c == null) {
            synchronized (this) {
                if (client == null) {
                    SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
                    factory.setConnectTimeout(Duration.ofSeconds(10));
                    factory.setReadTimeout(Duration.ofSeconds(30));
                    RestClient.Builder builder = RestClient.builder()
                            .baseUrl(baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl)
                            .requestFactory(new BufferingClientHttpRequestFactory(factory)) // sends Content-Length (some gateways reject chunked bodies)
                            .defaultHeader("Accept", "application/json");
                    if (apiKey != null && !apiKey.isBlank()) {
                        builder.defaultHeader("X-RapidAPI-Key", apiKey);
                        if (apiHost != null && !apiHost.isBlank()) {
                            builder.defaultHeader("X-RapidAPI-Host", apiHost);
                        }
                    }
                    if (authToken != null && !authToken.isBlank()) {
                        builder.defaultHeader("X-Auth-Token", authToken);
                    }
                    client = builder.build();
                }
                c = client;
            }
        }
        return c;
    }

    private static String b64(String s) {
        return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8));
    }

    private static String unb64(Object value) {
        if (value == null) return "";
        String s = value.toString();
        if (s.isEmpty()) return "";
        try {
            // MIME decoder ignores the line breaks Judge0 inserts into long base64 strings
            return new String(Base64.getMimeDecoder().decode(s), StandardCharsets.UTF_8);
        } catch (IllegalArgumentException e) {
            return s;
        }
    }
}
