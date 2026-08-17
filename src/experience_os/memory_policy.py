from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from experience_os.models import Experience


class MemoryAction(StrEnum):
    """
    Decision returned by the memory policy.
    """

    SAVE = "save"
    UPDATE = "update"
    IGNORE = "ignore"
    ARCHIVE = "archive"


@dataclass(slots=True, frozen=True)
class MemoryDecision:
    """
    Result of evaluating a memory.
    """

    action: MemoryAction
    reason: str


class MemoryPolicy:
    """
    Determines whether an experience should become
    long-term memory.

    Gen-1 uses simple heuristics.

    Future versions may use:
        - reinforcement learning
        - LLM reasoning
        - memory scoring
        - novelty detection
    """

    def __init__(
        self,
        *,
        minimum_confidence: float = 0.60,
        minimum_executions: int = 3,
    ) -> None:

        self._minimum_confidence = minimum_confidence
        self._minimum_executions = minimum_executions

    def evaluate(
        self,
        experience: Experience,
    ) -> MemoryDecision:
        """
        Decide how the memory should be handled.
        """

        # Very weak experiences are discarded.
        if experience.confidence < self._minimum_confidence:
            return MemoryDecision(
                action=MemoryAction.IGNORE,
                reason="confidence below threshold",
            )

        # Experiences with insufficient evidence
        # should continue accumulating observations.
        if experience.execution_count < self._minimum_executions:
            return MemoryDecision(
                action=MemoryAction.UPDATE,
                reason="insufficient evidence",
            )

        # Highly reliable memories are archived
        # as stable knowledge.
        if (
            experience.execution_count >= 100
            and experience.confidence >= 0.95
        ):
            return MemoryDecision(
                action=MemoryAction.ARCHIVE,
                reason="stable long-term knowledge",
            )

        return MemoryDecision(
            action=MemoryAction.SAVE,
            reason="meets memory policy",
        )

    def should_save(
        self,
        experience: Experience,
    ) -> bool:
        """
        Convenience helper.
        """

        return (
            self.evaluate(experience).action
            in (
                MemoryAction.SAVE,
                MemoryAction.UPDATE,
                MemoryAction.ARCHIVE,
            )
        )

    def is_archive_candidate(
        self,
        experience: Experience,
    ) -> bool:
        """
        True if the experience is mature enough
        for archival.
        """

        return (
            self.evaluate(experience).action
            is MemoryAction.ARCHIVE
        )

    @property
    def minimum_confidence(self) -> float:
        return self._minimum_confidence

    @property
    def minimum_executions(self) -> int:
        return self._minimum_executions