package com.learnsstream.controller;

import com.learnsstream.dto.MiscDtos.CertificateVerification;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.CertificateService;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/certificates")
public class CertificateController {

    private final CertificateService certificateService;

    public CertificateController(CertificateService certificateService) {
        this.certificateService = certificateService;
    }

    /** Downloads the PDF for the logged-in student (issued on first download if eligible). */
    @GetMapping("/course/{courseId}/download")
    public ResponseEntity<byte[]> download(@PathVariable Long courseId) {
        CertificateService.PdfFile file = certificateService.download(courseId, CurrentUser.get());
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDisposition(ContentDisposition.attachment().filename(file.fileName()).build());
        return ResponseEntity.ok().headers(headers).body(file.content());
    }

    /** Public: anyone (e.g. an employer) can check a certificate id. */
    @GetMapping("/verify/{serial}")
    public CertificateVerification verify(@PathVariable String serial) {
        return certificateService.verify(serial);
    }
}
