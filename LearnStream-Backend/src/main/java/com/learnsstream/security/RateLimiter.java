package com.learnsstream.security;

import com.learnsstream.exception.ApiException;
import org.springframework.stereotype.Component;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Small in-memory sliding-window rate limiter (per key, e.g. "login:1.2.3.4").
 * Good enough for a single server; use Redis if you ever run several instances.
 */
@Component
public class RateLimiter {

    private final Map<String, Deque<Long>> hits = new ConcurrentHashMap<>();

    /** Throws 429 if `key` was used more than `max` times in the last `windowSeconds`. */
    public void check(String key, int max, int windowSeconds, String message) {
        long now = System.currentTimeMillis();
        long windowStart = now - windowSeconds * 1000L;
        Deque<Long> deque = hits.computeIfAbsent(key, k -> new ArrayDeque<>());
        synchronized (deque) {
            while (!deque.isEmpty() && deque.peekFirst() < windowStart) {
                deque.pollFirst();
            }
            if (deque.size() >= max) {
                throw ApiException.tooManyRequests(message);
            }
            deque.addLast(now);
        }
        if (hits.size() > 50_000) {
            cleanup(windowStart);
        }
    }

    private void cleanup(long olderThan) {
        hits.entrySet().removeIf(e -> {
            synchronized (e.getValue()) {
                Long last = e.getValue().peekLast();
                return last == null || last < olderThan;
            }
        });
    }
}
