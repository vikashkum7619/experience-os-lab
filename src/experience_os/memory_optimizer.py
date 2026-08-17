from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from experience_os.models import Experience


@dataclass(slots=True, frozen=True)
class OptimizationReport:
    """
    Summary of a memory optimization pass.
    """

    original_count: int
    optimized_count: int
    removed_count: int


class MemoryOptimizer:
    """
    Optimizes collections of experiences.

    Gen-1 capabilities:

    - Remove low-confidence memories
    - Remove stale memories
    - Sort by importance

    Future versions may support:

    - Semantic clustering
    - Vector compression
    - Automatic summarization
    - LLM-assisted consolidation
    """

    def __init__(
        self,
        *,
        minimum_confidence: float = 0.60,
        maximum_age_days: int = 365,
    ) -> None:

        self._minimum_confidence = minimum_confidence
        self._maximum_age = timedelta(
            days=maximum_age_days,
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def optimize(
        self,
        experiences: list[Experience],
    ) -> tuple[list[Experience], OptimizationReport]:
        """
        Optimize a collection of experiences.
        """

        original = len(experiences)

        optimized = self.remove_low_confidence(
            experiences,
        )

        optimized = self.remove_stale(
            optimized,
        )

        optimized = self.sort_by_importance(
            optimized,
        )

        report = OptimizationReport(
            original_count=original,
            optimized_count=len(optimized),
            removed_count=original - len(optimized),
        )

        return optimized, report

    # ---------------------------------------------------------
    # Individual optimization passes
    # ---------------------------------------------------------

    def remove_low_confidence(
        self,
        experiences: list[Experience],
    ) -> list[Experience]:

        return [
            experience
            for experience in experiences
            if experience.confidence
            >= self._minimum_confidence
        ]

    def remove_stale(
        self,
        experiences: list[Experience],
    ) -> list[Experience]:

        now = datetime.now(UTC)

        return [
            experience
            for experience in experiences
            if (
                now - experience.updated_at
            ) <= self._maximum_age
        ]

    def sort_by_importance(
        self,
        experiences: list[Experience],
    ) -> list[Experience]:

        return sorted(
            experiences,
            key=lambda experience: (
                experience.confidence,
                experience.execution_count,
                experience.success_rate,
            ),
            reverse=True,
        )

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def minimum_confidence(
        self,
    ) -> float:

        return self._minimum_confidence

    @property
    def maximum_age_days(
        self,
    ) -> int:

        return self._maximum_age.days