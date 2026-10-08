package com.learnsstream.repository;

import com.learnsstream.entity.User;
import org.springframework.data.domain.Pageable;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmailIgnoreCase(String email);

    /** Row lock - used to stop double-claiming rewards or exceeding quiz attempts with parallel requests. */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT u FROM User u WHERE u.id = :id")
    Optional<User> lockById(@Param("id") Long id);

    boolean existsByEmailIgnoreCase(String email);

    long countByRole(String role);

    boolean existsByRole(String role);

    List<User> findByRole(String role);

    @Query("SELECT u FROM User u WHERE LOWER(u.fullName) LIKE LOWER(CONCAT('%', :q, '%')) " +
           "OR LOWER(u.email) LIKE LOWER(CONCAT('%', :q, '%')) ORDER BY u.createdAt DESC")
    List<User> search(@Param("q") String query, Pageable pageable);

    @Query("SELECT u FROM User u ORDER BY u.createdAt DESC")
    List<User> findRecent(Pageable pageable);
}
