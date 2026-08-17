from __future__ import annotations

from datetime import UTC, datetime, timedelta

from experience_os.models import Experience


class MemoryLifecycle:
    """
    Manages the lifecycle of experiences.

    Responsibilities
    ----------------
    - Strengthen successful experiences
    - Decay stale experiences
    - Decide whether an experience should be archived
    - Decide whether an experience should be forgotten
    """

    def __init__(
        self,
        *,
        confidence_decay: float = 0.98,
        strengthen_rate: float = 0.02,
        archive_threshold: float = 0.30,
        forget_threshold: float = 0.10,
        stale_after_days: int = 30,
    ) -> None:
        self._confidence_decay = confidence_decay
        self._strengthen_rate = strengthen_rate
        self._archive_threshold = archive_threshold
        self._forget_threshold = forget_threshold
        self._stale_after = timedelta(days=stale_after_days)

    # ---------------------------------------------------------
    # Strengthen
    # ---------------------------------------------------------

    def strengthen(
        self,
        experience: Experience,
    ) -> Experience:
        """
        Increase confidence for highly successful experiences.
        """

        if experience.success_rate >= 0.80:
            experience.confidence = min(
                1.0,
                experience.confidence + self._strengthen_rate,
            )

        experience.updated_at = datetime.now(UTC)

        return experience

    # ---------------------------------------------------------
    # Decay
    # ---------------------------------------------------------

    def decay(
        self,
        experience: Experience,
        *,
        now: datetime | None = None,
    ) -> Experience:
        """
        Reduce confidence of stale experiences.
        """

        now = now or datetime.now(UTC)

        age = now - experience.updated_at

        if age >= self._stale_after:
            experience.confidence *= self._confidence_decay

            experience.confidence = max(
                0.0,
                experience.confidence,
            )

            experience.updated_at = now

        return experience

    # ---------------------------------------------------------
    # Archive
    # ---------------------------------------------------------

    def should_archive(
        self,
        experience: Experience,
    ) -> bool:
        """
        Determine whether an experience should be archived.
        """

        return experience.confidence < self._archive_threshold

    # ---------------------------------------------------------
    # Forget
    # ---------------------------------------------------------

    def should_forget(
        self,
        experience: Experience,
    ) -> bool:
        """
        Determine whether an experience should be forgotten.
        """

        return experience.confidence < self._forget_threshold