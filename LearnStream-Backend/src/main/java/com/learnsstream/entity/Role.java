package com.learnsstream.entity;

/** Role names stored in the database and used as Spring Security authorities. */
public final class Role {
    public static final String STUDENT = "ROLE_STUDENT";
    public static final String ADMIN = "ROLE_ADMIN";

    private Role() {}

    public static boolean isValid(String role) {
        return STUDENT.equals(role) || ADMIN.equals(role);
    }
}
