package com.learnsstream.controller;

import com.learnsstream.service.VideoStorageService;
import org.springframework.core.io.Resource;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.time.Duration;

/**
 * Streams uploaded videos stored on local disk. The URL contains a signed, expiring token
 * (a browser's video player can't send our login header, so the link itself is the permission).
 * Spring handles HTTP Range requests automatically, so seeking works.
 */
@RestController
public class VideoController {

    private final VideoStorageService videoStorage;

    public VideoController(VideoStorageService videoStorage) {
        this.videoStorage = videoStorage;
    }

    @GetMapping("/api/videos/stream/{token}")
    public ResponseEntity<Resource> stream(@PathVariable String token) {
        Resource video = videoStorage.resolveToken(token);
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(VideoStorageService.contentTypeFor(video.getFilename())))
                .cacheControl(CacheControl.maxAge(Duration.ofHours(1)).cachePrivate())
                .header("X-Content-Type-Options", "nosniff")
                .body(video);
    }
}
