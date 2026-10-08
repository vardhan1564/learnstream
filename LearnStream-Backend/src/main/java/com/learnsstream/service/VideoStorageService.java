package com.learnsstream.service;

import com.learnsstream.exception.ApiException;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.core.checksums.RequestChecksumCalculation;
import software.amazon.awssdk.core.checksums.ResponseChecksumValidation;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.S3Configuration;
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.Base64;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * Stores uploaded lesson videos OUTSIDE the database (only the small file key like
 * "videos/3f2a....mp4" is saved on the lesson), and hands out expiring playback links.
 *
 *  - local: files on this server's disk; links point to /api/videos/stream/{signed-token}
 *  - s3:    Cloudflare R2 / AWS S3 / any S3-compatible bucket; links are S3 pre-signed URLs
 *
 * Expiring links mean a copied URL stops working after learnstream.storage.url-expiry-minutes.
 */
@Service
public class VideoStorageService {

    private static final Logger log = LoggerFactory.getLogger(VideoStorageService.class);

    /** Only keys we generated ourselves are accepted (prevents path traversal / pointing at other files). */
    public static final Pattern KEY_PATTERN = Pattern.compile("^videos/[a-f0-9-]{36}\\.(mp4|webm|mov|m4v|ogv)$");

    private static final Map<String, String> CONTENT_TYPES = Map.of(
            "mp4", "video/mp4", "m4v", "video/mp4", "webm", "video/webm", "mov", "video/quicktime", "ogv", "video/ogg");

    public record StoredVideo(String key, long size, String originalName) {}

    @Value("${learnstream.storage.type:local}")
    private String type;
    @Value("${learnstream.storage.local-dir:./uploads}")
    private String localDir;
    @Value("${learnstream.storage.s3.endpoint:}")
    private String s3Endpoint;
    @Value("${learnstream.storage.s3.region:auto}")
    private String s3Region;
    @Value("${learnstream.storage.s3.bucket:}")
    private String s3Bucket;
    @Value("${learnstream.storage.s3.access-key:}")
    private String s3AccessKey;
    @Value("${learnstream.storage.s3.secret-key:}")
    private String s3SecretKey;
    @Value("${learnstream.storage.url-expiry-minutes:240}")
    private long expiryMinutes;
    @Value("${learnstream.backend-url:http://localhost:8080}")
    private String backendUrl;
    @Value("${learnstream.jwt.secret}")
    private String signingSecret;

    private Path baseDir;
    private S3Client s3;
    private S3Presigner presigner;

    @PostConstruct
    void init() throws IOException {
        if (isS3()) {
            if (s3Bucket.isBlank() || s3AccessKey.isBlank() || s3SecretKey.isBlank()) {
                throw new IllegalStateException("learnstream.storage.type=s3 needs s3.bucket, s3.access-key and s3.secret-key");
            }
            StaticCredentialsProvider creds = StaticCredentialsProvider.create(AwsBasicCredentials.create(s3AccessKey, s3SecretKey));
            S3Configuration pathStyle = S3Configuration.builder().pathStyleAccessEnabled(true).build();
            var clientBuilder = S3Client.builder()
                    .region(Region.of(s3Region))
                    .credentialsProvider(creds)
                    .serviceConfiguration(pathStyle)
                    // R2 and several S3-compatible services don't support the newest default checksums
                    .requestChecksumCalculation(RequestChecksumCalculation.WHEN_REQUIRED)
                    .responseChecksumValidation(ResponseChecksumValidation.WHEN_REQUIRED);
            var presignerBuilder = S3Presigner.builder()
                    .region(Region.of(s3Region))
                    .credentialsProvider(creds)
                    .serviceConfiguration(pathStyle);
            if (!s3Endpoint.isBlank()) {
                clientBuilder.endpointOverride(URI.create(s3Endpoint));
                presignerBuilder.endpointOverride(URI.create(s3Endpoint));
            }
            s3 = clientBuilder.build();
            presigner = presignerBuilder.build();
            log.info("Video storage: S3-compatible bucket '{}'", s3Bucket);
        } else {
            baseDir = Path.of(localDir).toAbsolutePath().normalize();
            Files.createDirectories(baseDir.resolve("videos"));
            log.info("Video storage: local folder {}", baseDir);
        }
    }

    @PreDestroy
    void close() {
        if (s3 != null) s3.close();
        if (presigner != null) presigner.close();
    }

    public boolean isS3() {
        return "s3".equalsIgnoreCase(type);
    }

    /** Validates (type + real file signature) and stores the upload. Returns the key to save on the lesson. */
    public StoredVideo store(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw ApiException.badRequest("Choose a video file to upload");
        }
        String original = file.getOriginalFilename() == null ? "video" : Path.of(file.getOriginalFilename()).getFileName().toString();
        String ext = extension(original);
        if (!CONTENT_TYPES.containsKey(ext)) {
            throw ApiException.badRequest("Only MP4, WebM, MOV, M4V or OGV videos can be uploaded");
        }
        if (!looksLikeVideo(file)) {
            throw ApiException.badRequest("This file doesn't look like a real video. Please upload an MP4 or WebM file.");
        }
        String key = "videos/" + UUID.randomUUID() + "." + ext;
        try {
            if (isS3()) {
                Path temp = Files.createTempFile("ls-upload-", "." + ext);
                try {
                    file.transferTo(temp);
                    s3.putObject(PutObjectRequest.builder()
                                    .bucket(s3Bucket).key(key).contentType(CONTENT_TYPES.get(ext)).build(),
                            RequestBody.fromFile(temp));
                } finally {
                    Files.deleteIfExists(temp);
                }
            } else {
                Path target = resolveLocal(key);
                try (InputStream in = file.getInputStream()) {
                    Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
                }
            }
        } catch (IOException | RuntimeException e) {
            log.error("Video upload failed: {}", e.getMessage());
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "Could not save the video. Please try again.");
        }
        return new StoredVideo(key, file.getSize(), original);
    }

    /** Best-effort delete (used when a lesson or course is removed, or its video replaced). */
    public void delete(String key) {
        if (key == null || !KEY_PATTERN.matcher(key).matches()) return;
        try {
            if (isS3()) {
                s3.deleteObject(DeleteObjectRequest.builder().bucket(s3Bucket).key(key).build());
            } else {
                Files.deleteIfExists(resolveLocal(key));
            }
        } catch (Exception e) {
            log.warn("Could not delete video {}: {}", key, e.getMessage());
        }
    }

    /** A fresh, expiring link the browser's video player can load directly. */
    public String playbackUrl(String key) {
        if (key == null || !KEY_PATTERN.matcher(key).matches()) return null;
        Duration ttl = Duration.ofMinutes(Math.max(5, expiryMinutes));
        if (isS3()) {
            GetObjectPresignRequest req = GetObjectPresignRequest.builder()
                    .signatureDuration(ttl)
                    .getObjectRequest(r -> r.bucket(s3Bucket).key(key))
                    .build();
            return presigner.presignGetObject(req).url().toString();
        }
        long expires = System.currentTimeMillis() / 1000 + ttl.getSeconds();
        String payload = key + "|" + expires;
        String token = b64(payload.getBytes(StandardCharsets.UTF_8)) + "." + b64(hmac(payload));
        return trimSlash(backendUrl) + "/api/videos/stream/" + token;
    }

    /** Resolves a signed local token to the file, or throws 403 if the link is invalid or expired. */
    public Resource resolveToken(String token) {
        if (isS3()) throw ApiException.notFound("Video");
        String[] parts = token == null ? new String[0] : token.split("\\.");
        if (parts.length != 2) throw ApiException.forbidden("Invalid video link");
        String payload;
        try {
            payload = new String(Base64.getUrlDecoder().decode(parts[0]), StandardCharsets.UTF_8);
            byte[] given = Base64.getUrlDecoder().decode(parts[1]);
            if (!MessageDigest.isEqual(given, hmac(payload))) throw ApiException.forbidden("Invalid video link");
        } catch (IllegalArgumentException e) {
            throw ApiException.forbidden("Invalid video link");
        }
        int sep = payload.lastIndexOf('|');
        if (sep < 0) throw ApiException.forbidden("Invalid video link");
        String key = payload.substring(0, sep);
        long expires;
        try {
            expires = Long.parseLong(payload.substring(sep + 1));
        } catch (NumberFormatException e) {
            throw ApiException.forbidden("Invalid video link");
        }
        if (System.currentTimeMillis() / 1000 > expires) {
            throw ApiException.forbidden("This video link has expired. Reload the page to continue watching.");
        }
        if (!KEY_PATTERN.matcher(key).matches()) throw ApiException.forbidden("Invalid video link");
        Path file = resolveLocal(key);
        if (!Files.exists(file)) throw ApiException.notFound("Video");
        return new FileSystemResource(file);
    }

    public static String contentTypeFor(String filename) {
        return CONTENT_TYPES.getOrDefault(extension(filename), "application/octet-stream");
    }

    // ------------------------------------------------------------------

    private Path resolveLocal(String key) {
        Path p = baseDir.resolve(key).normalize();
        if (!p.startsWith(baseDir)) throw ApiException.forbidden("Invalid video path");
        return p;
    }

    /** Checks the first bytes: MP4/MOV have "ftyp" at offset 4, WebM starts with 1A 45 DF A3, Ogg with "OggS". */
    private static boolean looksLikeVideo(MultipartFile file) {
        try (InputStream in = file.getInputStream()) {
            byte[] h = in.readNBytes(12);
            if (h.length < 12) return false;
            boolean ftyp = h[4] == 'f' && h[5] == 't' && h[6] == 'y' && h[7] == 'p';
            boolean webm = (h[0] & 0xFF) == 0x1A && (h[1] & 0xFF) == 0x45 && (h[2] & 0xFF) == 0xDF && (h[3] & 0xFF) == 0xA3;
            boolean ogg = h[0] == 'O' && h[1] == 'g' && h[2] == 'g' && h[3] == 'S';
            return ftyp || webm || ogg;
        } catch (IOException e) {
            return false;
        }
    }

    private byte[] hmac(String payload) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(("video:" + signingSecret).getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            return mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private static String extension(String name) {
        int dot = name == null ? -1 : name.lastIndexOf('.');
        return dot < 0 ? "" : name.substring(dot + 1).toLowerCase(Locale.ROOT);
    }

    private static String b64(byte[] bytes) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private static String trimSlash(String s) {
        return s.endsWith("/") ? s.substring(0, s.length() - 1) : s;
    }
}
