package com.learnsstream.controller;

import com.learnsstream.dto.AuthDtos.LoginResponse;
import com.learnsstream.dto.AuthDtos.UserInfo;
import com.learnsstream.dto.CourseDtos.MyCourse;
import com.learnsstream.dto.MiscDtos.CertificateView;
import com.learnsstream.dto.RewardDtos.RewardStatus;
import com.learnsstream.dto.UserDtos.*;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.*;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users/me")
public class UserController {

    private final UserService userService;
    private final CourseService courseService;
    private final CertificateService certificateService;
    private final RewardService rewardService;

    public UserController(UserService userService, CourseService courseService,
                          CertificateService certificateService, RewardService rewardService) {
        this.userService = userService;
        this.courseService = courseService;
        this.certificateService = certificateService;
        this.rewardService = rewardService;
    }

    @GetMapping
    public ProfileResponse me() {
        return userService.profile(CurrentUser.get().id());
    }

    @PutMapping
    public UserInfo update(@Valid @RequestBody UpdateProfileRequest req) {
        return userService.updateProfile(CurrentUser.get().id(), req);
    }

    @PutMapping("/password")
    public LoginResponse changePassword(@Valid @RequestBody ChangePasswordRequest req) {
        return userService.changePassword(CurrentUser.get().id(), req);
    }

    @GetMapping("/courses")
    public List<MyCourse> myCourses() {
        return courseService.myCourses(CurrentUser.get().id());
    }

    @GetMapping("/certificates")
    public List<CertificateView> myCertificates() {
        return certificateService.myCertificates(CurrentUser.get().id());
    }

    @GetMapping("/rewards")
    public RewardStatus rewards() {
        return rewardService.statusFor(CurrentUser.get().id());
    }
}
