package com.learnsstream.security;

import com.learnsstream.entity.User;
import com.learnsstream.repository.UserRepository;
import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;

/**
 * Reads "Authorization: Bearer <token>", validates it and loads the user from the database,
 * so a deleted user or a changed role takes effect immediately (the role is never trusted from the token).
 */
public class JwtFilter extends OncePerRequestFilter {

    private final JwtUtils jwtUtils;
    private final UserRepository userRepository;

    public JwtFilter(JwtUtils jwtUtils, UserRepository userRepository) {
        this.jwtUtils = jwtUtils;
        this.userRepository = userRepository;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {

        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")
                && SecurityContextHolder.getContext().getAuthentication() == null) {
            Claims claims = jwtUtils.parse(header.substring(7).trim());
            if (claims != null && claims.getSubject() != null) {
                Date issuedAt = claims.getIssuedAt();
                userRepository.findByEmailIgnoreCase(claims.getSubject())
                        .filter(User::isVerified)
                        .filter(user -> user.getPasswordChangedAt() == null || (issuedAt != null
                                && !issuedAt.toInstant().isBefore(user.getPasswordChangedAt().atZone(ZoneId.systemDefault()).toInstant())))
                        .ifPresent(user -> {
                            AuthUser principal = new AuthUser(user.getId(), user.getEmail(), user.getRole());
                            UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                                    principal, null, List.of(new SimpleGrantedAuthority(user.getRole())));
                            SecurityContextHolder.getContext().setAuthentication(auth);
                        });
            }
        }
        chain.doFilter(request, response);
    }
}
