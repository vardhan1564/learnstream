package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "courses")
@Getter @Setter @NoArgsConstructor
public class Course {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    /** Price in rupees. 0 = free course. */
    @Column(nullable = false)
    private Double price = 0.0;

    @Column(length = 1000)
    private String thumbnail;

    @Column(length = 60)
    private String category;

    /** Beginner / Intermediate / Advanced */
    @Column(length = 30)
    private String level;

    @Column(length = 100)
    private String instructor;

    /** Unpublished courses are hidden from students (admins still see them). */
    @Column(nullable = false)
    private boolean published = true;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @OneToMany(mappedBy = "course", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("position ASC")
    private List<Lesson> lessons = new ArrayList<>();

    public boolean isFree() {
        return price == null || price <= 0;
    }
}
