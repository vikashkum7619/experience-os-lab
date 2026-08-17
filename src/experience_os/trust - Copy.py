from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExperienceEvidence:
    """
    Accumulated evidence for one experience.
    """

    executions: int = 0
    successes: int = 0
    failures: int = 0

    def record(self, success: bool) -> None:
        """Record one execution."""

        self.executions += 1

        if success:
            self.successes += 1
        else:
            self.failures += 1

    @property
    def success_rate(self) -> float:
        """Observed success rate."""

        if self.executions == 0:
            return 0.0

        return self.successes / self.executions


class EvidenceAccumulator:
    """
    Updates evidence after each execution.
    """

    def accumulate(
        self,
        evidence: ExperienceEvidence,
        *,
        success: bool,
    ) -> ExperienceEvidence:
        """
        Record one new observation.

        Returns the same evidence instance so callers can
        chain operations if desired.
        """

        evidence.record(success)

        return evidence


class TrustCalculator:
    """
    Converts evidence into a trust score.
    """

    def calculate(
        self,
        evidence: ExperienceEvidence,
    ) -> float:
        return evidence.success_rate