package com.learnsstream.service;

import com.learnsstream.dto.MiscDtos.CertificateVerification;
import com.learnsstream.dto.MiscDtos.CertificateView;
import com.learnsstream.entity.Certificate;
import com.learnsstream.entity.Course;
import com.learnsstream.entity.User;
import com.learnsstream.exception.ApiException;
import com.learnsstream.repository.CertificateRepository;
import com.learnsstream.repository.EnrollmentRepository;
import com.learnsstream.repository.UserRepository;
import com.learnsstream.security.AuthUser;
import com.lowagie.text.Document;
import com.lowagie.text.Element;
import com.lowagie.text.Image;
import com.lowagie.text.PageSize;
import com.lowagie.text.pdf.BaseFont;
import com.lowagie.text.pdf.PdfContentByte;
import com.lowagie.text.pdf.PdfWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.security.SecureRandom;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;

@Service
public class CertificateService {

    private static final Logger log = LoggerFactory.getLogger(CertificateService.class);
    private static final String SERIAL_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

    private final SecureRandom random = new SecureRandom();
    private final CertificateRepository certificateRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository;
    private final CourseService courseService;

    @Value("${learnstream.frontend-url}")
    private String frontendUrl;

    public CertificateService(CertificateRepository certificateRepository, EnrollmentRepository enrollmentRepository,
                              UserRepository userRepository, CourseService courseService) {
        this.certificateRepository = certificateRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.userRepository = userRepository;
        this.courseService = courseService;
    }

    public record PdfFile(String fileName, byte[] content) {}

    @Transactional(readOnly = true)
    public List<CertificateView> myCertificates(Long userId) {
        return certificateRepository.findByUserIdWithCourse(userId).stream()
                .map(c -> new CertificateView(c.getSerialNumber(), c.getCourse().getId(), c.getCourse().getTitle(), c.getIssuedAt()))
                .toList();
    }

    /** Issues the certificate on first download (only if eligible) and returns the PDF. */
    @Transactional
    public PdfFile download(Long courseId, AuthUser viewer) {
        Course course = courseService.requireCourse(courseId);
        if (!enrollmentRepository.existsByUserIdAndCourseId(viewer.id(), courseId)) {
            throw ApiException.forbidden("You are not enrolled in this course");
        }
        Certificate cert = certificateRepository.findByUserIdAndCourseId(viewer.id(), courseId).orElse(null);
        if (cert == null) {
            var progress = courseService.progress(viewer.id(), course);
            if (!progress.certificateEligible()) {
                String reason;
                if (progress.totalCount() == 0) {
                    reason = "This course has no lessons yet, so a certificate can't be issued.";
                } else if (progress.completedCount() < progress.totalCount()) {
                    reason = "Complete all " + progress.totalCount() + " lessons to unlock your certificate ("
                            + progress.completedCount() + " done).";
                } else {
                    reason = "Pass the course quiz to unlock your certificate.";
                }
                throw ApiException.forbidden(reason);
            }
            User user = userRepository.findById(viewer.id()).orElseThrow(() -> ApiException.notFound("User"));
            cert = new Certificate();
            cert.setUser(user);
            cert.setCourse(course);
            cert.setSerialNumber(newSerial());
            cert = certificateRepository.save(cert);
        }
        byte[] pdf = render(cert.getUser().getFullName(), course.getTitle(), cert.getSerialNumber(),
                cert.getIssuedAt().toLocalDate());
        String safeName = course.getTitle().replaceAll("[^A-Za-z0-9]+", "_");
        return new PdfFile("LearnStream_" + safeName + "_Certificate.pdf", pdf);
    }

    @Transactional(readOnly = true)
    public CertificateVerification verify(String serial) {
        return certificateRepository.findBySerialWithDetails(serial.trim().toUpperCase(Locale.ROOT))
                .map(c -> new CertificateVerification(true, c.getSerialNumber(), c.getUser().getFullName(),
                        c.getCourse().getTitle(), c.getIssuedAt()))
                .orElse(new CertificateVerification(false, serial, null, null, null));
    }

    private String newSerial() {
        String date = LocalDate.now().format(DateTimeFormatter.BASIC_ISO_DATE);
        for (int attempt = 0; attempt < 10; attempt++) {
            StringBuilder sb = new StringBuilder("LS-").append(date).append('-');
            for (int i = 0; i < 8; i++) {
                sb.append(SERIAL_CHARS.charAt(random.nextInt(SERIAL_CHARS.length())));
            }
            String serial = sb.toString();
            if (!certificateRepository.existsBySerialNumber(serial)) {
                return serial;
            }
        }
        throw new IllegalStateException("Could not generate a unique certificate serial");
    }

    // ---------------------------------------------------------------- PDF

    private byte[] render(String studentName, String courseTitle, String serial, LocalDate issuedOn) {
        try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            Document document = new Document(PageSize.A4.rotate(), 0, 0, 0, 0);
            PdfWriter writer = PdfWriter.getInstance(document, out);
            document.open();

            PdfContentByte cb = writer.getDirectContent();
            PdfContentByte under = writer.getDirectContentUnder(); // background layer, below images and text
            float w = document.getPageSize().getWidth();
            float h = document.getPageSize().getHeight();

            Color ink = new Color(17, 24, 39);
            Color accent = new Color(27, 91, 208); // LearnStream blue
            Color gold = new Color(202, 160, 60);
            Color muted = new Color(100, 116, 139);

            // Background + double border
            under.saveState();
            under.setColorFill(Color.WHITE); // white so the logo and stamp images blend in
            under.rectangle(0, 0, w, h);
            under.fill();
            under.setColorFill(accent);
            under.rectangle(0, h - 14, w, 14);
            under.fill();
            under.rectangle(0, 0, w, 14);
            under.fill();
            under.setColorStroke(gold);
            under.setLineWidth(3f);
            under.rectangle(30, 30, w - 60, h - 60);
            under.stroke();
            under.setLineWidth(0.8f);
            under.rectangle(38, 38, w - 76, h - 76);
            under.stroke();
            under.restoreState();

            addImage(cb, "static/images/Logo.png", 220, 52, (w - 220) / 2, h - 125);

            BaseFont serif = BaseFont.createFont(BaseFont.TIMES_ROMAN, BaseFont.CP1252, BaseFont.NOT_EMBEDDED);
            BaseFont serifBold = BaseFont.createFont(BaseFont.TIMES_BOLD, BaseFont.CP1252, BaseFont.NOT_EMBEDDED);
            BaseFont serifItalic = BaseFont.createFont(BaseFont.TIMES_ITALIC, BaseFont.CP1252, BaseFont.NOT_EMBEDDED);
            BaseFont sans = BaseFont.createFont(BaseFont.HELVETICA, BaseFont.CP1252, BaseFont.NOT_EMBEDDED);
            BaseFont sansBold = BaseFont.createFont(BaseFont.HELVETICA_BOLD, BaseFont.CP1252, BaseFont.NOT_EMBEDDED);

            float cx = w / 2;
            text(cb, sansBold, 13, accent, "CERTIFICATE OF COMPLETION", cx, h - 165, 3f);
            text(cb, serifItalic, 16, muted, "This is to certify that", cx, h - 205, 0);
            text(cb, serifBold, fitSize(serifBold, studentName, 40, w - 200), ink, studentName, cx, h - 255, 0);

            cb.setColorStroke(gold);
            cb.setLineWidth(1f);
            cb.moveTo(cx - 200, h - 270);
            cb.lineTo(cx + 200, h - 270);
            cb.stroke();

            text(cb, serifItalic, 16, muted, "has successfully completed the course", cx, h - 300, 0);
            text(cb, serifBold, fitSize(serifBold, courseTitle, 28, w - 200), accent, courseTitle, cx, h - 340, 0);
            text(cb, serif, 13, muted, "on LearnStream, demonstrating dedication to learning and growth.", cx, h - 368, 0);

            // Footer: date (left), signature (centre), stamp (right)
            float footerY = 120;
            line(cb, 110, footerY, 290, footerY, muted);
            text(cb, sansBold, 12, ink, issuedOn.format(DateTimeFormatter.ofPattern("dd MMMM yyyy", Locale.ENGLISH)), 200, footerY + 10, 0);
            text(cb, sans, 10, muted, "Date of issue", 200, footerY - 16, 0);

            line(cb, cx - 90, footerY, cx + 90, footerY, muted);
            text(cb, serifItalic, 18, ink, "LearnStream", cx, footerY + 10, 0);
            text(cb, sans, 10, muted, "Director of Learning", cx, footerY - 16, 0);

            addImage(cb, "static/images/Stamp.png", 120, 120, w - 230, footerY - 50);

            text(cb, sans, 9, muted, "Certificate ID: " + serial + "   |   Verify at " + frontendUrl + "/verify/" + serial,
                    cx, 50, 0);

            document.close();
            return out.toByteArray();
        } catch (Exception e) {
            log.error("Certificate generation failed", e);
            throw new IllegalStateException("Could not generate certificate", e);
        }
    }

    private static void text(PdfContentByte cb, BaseFont font, float size, Color color, String value,
                             float x, float y, float charSpacing) {
        cb.beginText();
        cb.setFontAndSize(font, size);
        cb.setColorFill(color);
        cb.setCharacterSpacing(charSpacing);
        cb.showTextAligned(Element.ALIGN_CENTER, value, x, y, 0);
        cb.setCharacterSpacing(0);
        cb.endText();
    }

    private static void line(PdfContentByte cb, float x1, float y1, float x2, float y2, Color color) {
        cb.saveState();
        cb.setColorStroke(color);
        cb.setLineWidth(0.6f);
        cb.moveTo(x1, y1);
        cb.lineTo(x2, y2);
        cb.stroke();
        cb.restoreState();
    }

    /** Shrinks long names / titles so they always fit on the page. */
    private static float fitSize(BaseFont font, String value, float max, float maxWidth) {
        float size = max;
        while (size > 12 && font.getWidthPoint(value, size) > maxWidth) {
            size -= 1;
        }
        return size;
    }

    private void addImage(PdfContentByte cb, String path, float maxW, float maxH, float x, float y) {
        try (InputStream is = getClass().getClassLoader().getResourceAsStream(path)) {
            if (is == null) {
                log.warn("Certificate image not found on classpath: {}", path);
                return;
            }
            Image img = Image.getInstance(is.readAllBytes());
            img.scaleToFit(maxW, maxH);
            img.setAbsolutePosition(x + (maxW - img.getScaledWidth()) / 2, y + (maxH - img.getScaledHeight()) / 2);
            cb.addImage(img);
        } catch (Exception e) {
            log.warn("Could not add {} to certificate: {}", path, e.getMessage());
        }
    }
}
