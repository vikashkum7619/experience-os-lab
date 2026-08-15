from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from experience_os.models import OutcomeStatus


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(UTC)


@dataclass(frozen=True)
class TraceStep:
    """
    One execution step.

    A step may represent:
    - a planner decision
    - a tool call
    - an LLM response
    - a validation
    """

    id: UUID = field(default_factory=uuid4)

    name: str = ""

    input: dict[str, Any] = field(
        default_factory=dict,
    )

    output: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    created_at: datetime = field(
        default_factory=utc_now,
    )


@dataclass
class ExecutionTrace:
    """
    Records one complete execution.

    This becomes the source of learning.
    """

    id: UUID = field(default_factory=uuid4)

    task_goal: str = ""

    task_context: dict[str, Any] = field(
        default_factory=dict,
    )

    steps: list[TraceStep] = field(
        default_factory=list,
    )

    status: OutcomeStatus = OutcomeStatus.SUCCESS

    score: float = 1.0

    started_at: datetime = field(
        default_factory=utc_now,
    )

    finished_at: datetime | None = None

    # --------------------------------------------------
    # Recording
    # --------------------------------------------------

    def add_step(
        self,
        step: TraceStep,
    ) -> None:
        """Append a step."""
        self.steps.append(step)

    def record(
        self,
        *,
        name: str,
        input: dict[str, Any] | None = None,
        output: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TraceStep:
        """
        Convenience helper.
        """

        step = TraceStep(
            name=name,
            input=input or {},
            output=output or {},
            metadata=metadata or {},
        )

        self.steps.append(step)

        return step

    # --------------------------------------------------
    # Completion
    # --------------------------------------------------

    def finish(
        self,
        *,
        status: OutcomeStatus,
        score: float,
    ) -> None:
        """
        Mark execution complete.
        """

        self.status = status
        self.score = score
        self.finished_at = utc_now()

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def successful(self) -> bool:
        return self.status == OutcomeStatus.SUCCESS

    @property
    def duration_seconds(self) -> float | None:
        if self.finished_at is None:
            return None

        return (
            self.finished_at - self.started_at
        ).total_seconds()

    # --------------------------------------------------
    # Export
    # --------------------------------------------------

    def decision_pattern(self) -> list[str]:
        """
        Convert trace into reusable decision sequence.
        """

        return [
            step.name
            for step in self.steps
        ]

    def clear(self) -> None:
        """
        Reset trace.
        """

        self.steps.clear()

        self.finished_at = None

        self.score = 1.0

        self.status = OutcomeStatus.SUCCESS