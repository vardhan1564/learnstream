package com.learnsstream.dto;

public final class RewardDtos {

    private RewardDtos() {}

    public record RewardStatus(
            long problemsSolved,
            int problemsPerFreeCourse,
            long creditsEarned,
            long creditsUsed,
            long creditsAvailable,
            long problemsToNextCredit) {}
}
