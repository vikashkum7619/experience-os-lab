from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from experience_os.models import Experience


class ExperienceState(StrEnum):
    """
    Lifecycle state of an experience.

    CANDIDATE
        Newly learned experience with insufficient evidence.

    VALIDATED
        Proven through repeated successful executions.

    TRUSTED
        High-confidence experience suitable for regular reuse.

    EXPERT
        Extremely reliable experience representing best practice.

    RETIRED
        Confidence has fallen too low and the experience should
        no longer be reused.

    ARCHIVED
        Permanently retained for historical purposes.
    """

    CANDIDATE = "candidate"
    VALIDATED = "validated"
    TRUSTED = "trusted"
    EXPERT = "expert"
    RETIRED = "retired"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class LifecyclePolicy:
    """
    Promotion and retirement thresholds.
    """

    validated_threshold: float = 0.60
    trusted_threshold: float = 0.80
    expert_threshold: float = 0.95

    retire_threshold: float = 0.30

    minimum_executions: int = 5


class ExperienceLifecycle:
    """
    Determines the lifecycle state of an experience.

    Gen-1 rules

    • insufficient executions -> CANDIDATE
    • low confidence -> RETIRED
    • otherwise promote according to confidence
    """

    def __init__(
        self,
        policy: LifecyclePolicy | None = None,
    ) -> None:
        self._policy = policy or LifecyclePolicy()

    def state(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Determine lifecycle state.
        """

        if experience.execution_count == 0:
            return ExperienceState.CANDIDATE

        if (
            experience.execution_count
            < self._policy.minimum_executions
        ):
            return ExperienceState.CANDIDATE

        confidence = experience.confidence

        if confidence < self._policy.retire_threshold:
            return ExperienceState.RETIRED

        if confidence >= self._policy.expert_threshold:
            return ExperienceState.EXPERT

        if confidence >= self._policy.trusted_threshold:
            return ExperienceState.TRUSTED

        if confidence >= self._policy.validated_threshold:
            return ExperienceState.VALIDATED

        return ExperienceState.CANDIDATE

    def is_active(
        self,
        experience: Experience,
    ) -> bool:
        """
        Whether an experience can participate in planning.
        """

        return self.state(experience) not in (
            ExperienceState.RETIRED,
            ExperienceState.ARCHIVED,
        )

    def should_promote(
        self,
        experience: Experience,
    ) -> bool:
        """
        Whether the experience has reached VALIDATED or above.
        """

        return self.state(experience) in (
            ExperienceState.VALIDATED,
            ExperienceState.TRUSTED,
            ExperienceState.EXPERT,
        )

    def should_retire(
        self,
        experience: Experience,
    ) -> bool:
        """
        Whether the experience should be retired.
        """

        return (
            self.state(experience)
            == ExperienceState.RETIRED
        )

    def archive(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Archive an experience.

        Future versions will update ExperienceMemory.
        """

        del experience

        return ExperienceState.ARCHIVED

    def promote(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Return promoted lifecycle state.
        """

        return self.state(experience)

    def demote(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Recompute lifecycle after confidence changes.
        """

        return self.state(experience)

    def refresh(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Refresh lifecycle after new evidence.
        """

        return self.state(experience)