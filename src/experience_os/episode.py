from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    Task,
)
from experience_os.reflection import Reflection


def utc_now() -> datetime:
    """
    Return the current UTC timestamp.
    """
    return datetime.now(UTC)


class Episode(BaseModel):
    """
    Complete record of a single agent execution.

    Unlike an Experience, which represents distilled knowledge,
    an Episode preserves the entire execution history that
    produced the experience.
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)

    task: Task

    decision: Decision

    outcome: Outcome

    reflection: Reflection

    experience: Experience

    created_at: datetime = Field(default_factory=utc_now)

    @property
    def success(self) -> bool:
        """
        Whether the execution succeeded.
        """
        return self.outcome.status.value == "success"

    @property
    def score(self) -> float:
        """
        Convenience accessor for the outcome score.
        """
        return self.outcome.score

    @property
    def confidence(self) -> float:
        """
        Confidence of the learned experience.
        """
        return self.experience.confidence