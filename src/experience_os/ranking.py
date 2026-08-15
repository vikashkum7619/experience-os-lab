from __future__ import annotations

from dataclasses import dataclass

from experience_os.models import Experience, Task


@dataclass(frozen=True)
class ExperienceScore:
    """Ranking result for one experience."""

    experience: Experience
    similarity: float
    trust: float
    total_score: float


class ExperienceRanker:
    """Ranks recalled experiences."""

    def score(
        self,
        experience: Experience,
        task: Task,
    ) -> ExperienceScore:
        similarity = self._similarity(
            experience,
            task,
        )

        trust = experience.confidence

        total = (
            similarity * 0.6
            + trust * 0.4
        )

        return ExperienceScore(
            experience=experience,
            similarity=similarity,
            trust=trust,
            total_score=total,
        )

    def rank(
        self,
        experiences: list[Experience],
        task: Task,
    ) -> list[ExperienceScore]:
        scores = [
            self.score(exp, task)
            for exp in experiences
        ]

        return sorted(
            scores,
            key=lambda score: score.total_score,
            reverse=True,
        )

    def _similarity(
        self,
        experience: Experience,
        task: Task,
    ) -> float:
        if not experience.conditions:
            return 0.0

        matched = 0

        for key, value in experience.conditions.items():
            if task.context.get(key) == value:
                matched += 1

        return matched / len(experience.conditions)