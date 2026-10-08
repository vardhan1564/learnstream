package com.learnsstream.repository;

import com.learnsstream.entity.Payment;
import org.springframework.data.domain.Pageable;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface PaymentRepository extends JpaRepository<Payment, Long> {

    Optional<Payment> findByStripeSessionId(String sessionId);

    /** Row lock so the success page and the Stripe webhook can't fulfil the same payment at once. */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Payment p WHERE p.stripeSessionId = :sessionId")
    Optional<Payment> lockBySessionId(@Param("sessionId") String sessionId);

    @Query("SELECT COALESCE(SUM(p.amount), 0) FROM Payment p WHERE p.status = 'PAID'")
    long sumPaidAmount();

    @Query("SELECT p FROM Payment p JOIN FETCH p.user JOIN FETCH p.course WHERE p.status = 'PAID' ORDER BY p.paidAt DESC")
    List<Payment> findRecentPaid(Pageable pageable);

    @Modifying
    @Query("DELETE FROM Payment p WHERE p.course.id = :courseId AND p.status <> 'PAID'")
    void deleteUnpaidByCourseId(@Param("courseId") Long courseId);
}
