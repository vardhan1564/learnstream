package com.learnsstream.controller;

import com.learnsstream.dto.MiscDtos.LeaderboardEntry;
import com.learnsstream.security.AuthUser;
import com.learnsstream.security.CurrentUser;
import com.learnsstream.service.AdminService;
import com.learnsstream.service.LeaderboardService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class LeaderboardController {

    private final LeaderboardService leaderboardService;
    private final AdminService adminService;

    public LeaderboardController(LeaderboardService leaderboardService, AdminService adminService) {
        this.leaderboardService = leaderboardService;
        this.adminService = adminService;
    }

    /** Logged-in students see names and points; emails are only shown to admins. */
    @GetMapping("/api/leaderboard")
    public List<LeaderboardEntry> leaderboard(@RequestParam(defaultValue = "50") int limit) {
        AuthUser viewer = CurrentUser.get();
        return leaderboardService.leaderboard(limit, viewer, viewer.isAdmin());
    }

    @GetMapping("/api/stats/public")
    public Map<String, Long> publicStats() {
        return adminService.publicStats();
    }
}
