package com.learnsstream.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "lessons")
@Getter @Setter @NoArgsConstructor
public class Lesson {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    /** External video link (YouTube, Vimeo, Google Drive, direct .mp4). Null when the video was uploaded. */
    @Column(length = 1000)
    private String videoUrl;

    /** Storage key of an uploaded video, e.g. "videos/<uuid>.mp4". The file itself lives on disk / in R2-S3, never in the DB. */
    @Column(length = 100)
    private String videoFileKey;

    /** Original file name of the upload (shown to admins). */
    @Column(length = 255)
    private String videoFileName;

    private Integer durationMinutes;

    @Column(nullable = false)
    private int position = 0;

    /** Free preview lessons can be watched without buying the course. */
    @Column(nullable = false)
    private boolean preview = false;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "course_id", nullable = false)
    private Course course;
}
