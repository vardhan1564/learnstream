package com.learnsstream.security;

/** The logged-in user, stored as the Spring Security principal. */
public record AuthUser(Long id, String email, String role) {

    public boolean isAdmin() {
        return com.learnsstream.entity.Role.ADMIN.equals(role);
    }
}
