package com.learnsstream.repository;

import com.learnsstream.entity.Certificate;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface CertificateRepository extends JpaRepository<Certificate, Long> {

    Optional<Certificate> findByUserIdAndCourseId(Long userId, Long courseId);

    @Query("SELECT c FROM Certificate c JOIN FETCH c.user JOIN FETCH c.course WHERE c.serialNumber = :serial")
    Optional<Certificate> findBySerialWithDetails(@Param("serial") String serial);

    @Query("SELECT c FROM Certificate c JOIN FETCH c.course WHERE c.user.id = :userId ORDER BY c.issuedAt DESC")
    List<Certificate> findByUserIdWithCourse(@Param("userId") Long userId);

    boolean existsBySerialNumber(String serialNumber);

    long countByCourseId(Long courseId);
}
