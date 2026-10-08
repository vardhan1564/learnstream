package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "roadmap_progress", uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "step_id"}))
@Getter @Setter @NoArgsConstructor
public class RoadmapProgress {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "step_id", nullable = false)
    private RoadmapStep step;

    @Column(nullable = false)
    private LocalDateTime completedAt = LocalDateTime.now();
}
