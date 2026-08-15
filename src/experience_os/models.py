from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(UTC)


class Task(BaseModel):
    """A business objective that an agent is trying to accomplish."""

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    goal: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class Decision(BaseModel):
    """A meaningful choice made during task execution."""

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    description: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    alternatives: list[str] = Field(default_factory=list)


class OutcomeStatus(StrEnum):
    """Possible execution outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"

class ApplicabilityStatus(StrEnum):
    """Decision about whether an experience applies to a task."""

    APPLY = "apply"
    UNCERTAIN = "uncertain"
    REJECT = "reject"


class ApplicabilityResult(BaseModel):
    """Result of evaluating whether an experience applies."""

    model_config = ConfigDict(extra="forbid")

    status: ApplicabilityStatus
    matched_conditions: list[str] = Field(default_factory=list)
    mismatched_conditions: list[str] = Field(default_factory=list)
    uncertain_conditions: list[str] = Field(default_factory=list)
    reason: str = Field(min_length=1)

class Outcome(BaseModel):
    """The measurable result of an execution."""

    model_config = ConfigDict(extra="forbid")

    status: OutcomeStatus
    score: float = Field(ge=0.0, le=1.0)
    metrics: dict[str, float] = Field(default_factory=dict)
    description: str = Field(min_length=1)


class Experience(BaseModel):
    """
    A reusable decision pattern derived from previous executions.

    Experience is not raw conversation history. It is a decision pattern
    supported by evidence from previous executions.
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)

    # Conditions under which this experience may be applicable.
    conditions: dict[str, Any] = Field(default_factory=dict)

    # Reusable sequence of decisions.
    decision_pattern: list[str] = Field(min_length=1)

    # Evidence accumulated from previous executions.
    execution_count: int = Field(default=0, ge=0)
    successful_executions: int = Field(default=0, ge=0)

    # Confidence is bounded between 0 and 1.
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def success_rate(self) -> float:
        """Return the observed success rate of this experience."""
        if self.execution_count == 0:
            return 0.0

        return self.successful_executions / self.execution_count