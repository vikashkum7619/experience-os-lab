from __future__ import annotations

from uuid import UUID

from experience_os.models import (
    ApplicabilityResult,
    ApplicabilityStatus,
    Experience,
    Task,
)


class ExperienceStore:
    """
    Simple in-memory experience store.

    Gen-1 intentionally avoids databases and vector search.

    The objective is to validate the Experience OS pipeline
    before introducing persistence or embeddings.
    """

    def __init__(self) -> None:
        self._experiences: list[Experience] = []

    def add(
        self,
        experience: Experience,
    ) -> None:
        """Store one experience."""
        self._experiences.append(experience)

    def get(
        self,
        experience_id: UUID,
    ) -> Experience | None:
        """Return an experience by ID."""

        for experience in self._experiences:
            if experience.id == experience_id:
                return experience

        return None

    def exists(
        self,
        experience_id: UUID,
    ) -> bool:
        """Return True if the experience exists."""

        return self.get(experience_id) is not None

    def update(
        self,
        experience: Experience,
    ) -> bool:
        """Replace an existing experience."""

        for index, current in enumerate(self._experiences):
            if current.id == experience.id:
                self._experiences[index] = experience
                return True

        return False

    def remove(
        self,
        experience_id: UUID,
    ) -> bool:
        """Remove an experience."""

        for index, experience in enumerate(self._experiences):
            if experience.id == experience_id:
                del self._experiences[index]
                return True

        return False

    def count(
        self,
    ) -> int:
        """Return the number of stored experiences."""

        return len(self._experiences)

    def clear(
        self,
    ) -> None:
        """Remove every stored experience."""

        self._experiences.clear()

    def all(
        self,
    ) -> list[Experience]:
        """Return every stored experience."""

        return list(self._experiences)


class ExperienceRecall:
    """
    Retrieve candidate experiences.

    IMPORTANT

    Recall DOES NOT determine whether an experience is safe.

    Recall only answers:

        "Which experiences might be relevant?"

    Applicability later answers:

        "Can this experience actually be reused?"

    This separation becomes important when semantic/vector
    retrieval is introduced.
    """

    def __init__(
        self,
        store: ExperienceStore,
    ) -> None:
        self._store = store

    def recall(
        self,
        task: Task,
    ) -> list[Experience]:
        """
        Return candidate experiences.

        Gen-1 strategy:

        An experience is considered a candidate if at least
        one experience condition matches the task context.

        Candidate retrieval is intentionally broad.

        Final reuse is decided later by
        ExperienceApplicability.
        """

        candidates: list[Experience] = []

        for experience in self._store.all():
            if self._has_relevant_overlap(
                experience,
                task,
            ):
                candidates.append(experience)

        return candidates

    def _has_relevant_overlap(
        self,
        experience: Experience,
        task: Task,
    ) -> bool:
        """
        Return True when at least one condition matches.
        """

        for key, expected_value in experience.conditions.items():
            if task.context.get(key) == expected_value:
                return True

        return False


class ExperienceApplicability:
    """
    Determine whether a recalled experience can be reused.

    APPLY

        Every experience condition matches.

    REJECT

        One or more conditions contradict the task.

    UNCERTAIN

        No conflicts exist, but required information is missing.
    """

    def evaluate(
        self,
        experience: Experience,
        task: Task,
    ) -> ApplicabilityResult:
        """Evaluate one candidate experience."""

        matched: list[str] = []
        mismatched: list[str] = []
        uncertain: list[str] = []

        for key, expected_value in experience.conditions.items():
            if key not in task.context:
                uncertain.append(key)
                continue

            actual_value = task.context[key]

            if actual_value == expected_value:
                matched.append(key)
            else:
                mismatched.append(key)

        if mismatched:
            return ApplicabilityResult(
                status=ApplicabilityStatus.REJECT,
                matched_conditions=matched,
                mismatched_conditions=mismatched,
                uncertain_conditions=uncertain,
                reason=(
                    "One or more experience conditions "
                    "contradict the task."
                ),
            )

        if uncertain:
            return ApplicabilityResult(
                status=ApplicabilityStatus.UNCERTAIN,
                matched_conditions=matched,
                mismatched_conditions=mismatched,
                uncertain_conditions=uncertain,
                reason=(
                    "The task does not provide all conditions "
                    "required to validate the experience."
                ),
            )

        return ApplicabilityResult(
            status=ApplicabilityStatus.APPLY,
            matched_conditions=matched,
            mismatched_conditions=mismatched,
            uncertain_conditions=uncertain,
            reason="All experience conditions match the task.",
        )