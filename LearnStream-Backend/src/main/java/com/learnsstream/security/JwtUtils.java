package com.learnsstream.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;

@Component
public class JwtUtils {

    @Value("${learnstream.jwt.secret}")
    private String jwtSecret;

    @Value("${learnstream.jwt.expiration-hours:24}")
    private long expirationHours;

    private Key signingKey;

    @PostConstruct
    void init() {
        if (jwtSecret == null || jwtSecret.length() < 32) {
            throw new IllegalStateException("learnstream.jwt.secret must be at least 32 characters long");
        }
        if (jwtSecret.startsWith("change-me")) {
            throw new IllegalStateException("Set your own learnstream.jwt.secret (or JWT_SECRET) - the placeholder value is public. "
                    + "Generate one with: openssl rand -hex 32");
        }
        signingKey = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }

    public String generateToken(Long userId, String email, String role) {
        Date now = new Date();
        return Jwts.builder()
                .setSubject(email)
                .claim("uid", userId)
                .claim("role", role)
                .setIssuedAt(now)
                .setExpiration(new Date(now.getTime() + expirationHours * 3600_000L))
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();
    }

    /** Returns the claims if the token is valid and not expired, otherwise null. */
    public Claims parse(String token) {
        try {
            return Jwts.parserBuilder().setSigningKey(signingKey).build().parseClaimsJws(token).getBody();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }
}
