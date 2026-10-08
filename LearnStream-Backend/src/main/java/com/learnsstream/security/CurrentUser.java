package com.learnsstream.security;

import com.learnsstream.exception.ApiException;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

/** Helpers to read the logged-in user anywhere in the code. */
public final class CurrentUser {

    private CurrentUser() {}

    /** The logged-in user, or null for anonymous visitors. */
    public static AuthUser getOrNull() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof AuthUser user) {
            return user;
        }
        return null;
    }

    /** The logged-in user, or a 401 error. */
    public static AuthUser get() {
        AuthUser user = getOrNull();
        if (user == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "Please log in to continue");
        }
        return user;
    }
}
