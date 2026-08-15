from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Protocol

from experience_os.models import (
    Decision,
    Outcome,
    OutcomeStatus,
    Task,
)


# ==========================================================
# Execution Backend
# ==========================================================

class ExecutionBackend(Protocol):
    """
    Interface implemented by execution backends.
    """

    def execute(
        self,
        task: Task,
        decision: Decision,
    ) -> Outcome: ...


# ==========================================================
# Default Rule-Based Backend
# ==========================================================

@dataclass(slots=True)
class RuleBasedExecutor:
    """
    Simple deterministic executor.
    """

    def execute(
        self,
        task: Task,
        decision: Decision,
    ) -> Outcome:
        del task

        description = decision.description.lower()

        # --------------------------------------------------
        # Success conditions
        # --------------------------------------------------
        if (
            "total trip cost" in description
            or "trip cost" in description
            or "total cost" in description
        ):
            return Outcome(
                status=OutcomeStatus.SUCCESS,
                score=1.0,
                metrics={
                    "execution_time_ms": 25.0,
                    "confidence": 1.0,
                },
                description=(
                    "Execution completed successfully "
                    "using total-cost comparison."
                ),
            )

        # --------------------------------------------------
        # Default outcome
        # --------------------------------------------------
        return Outcome(
            status=OutcomeStatus.PARTIAL,
            score=0.60,
            metrics={
                "execution_time_ms": 25.0,
                "confidence": 0.60,
            },
            description="Execution completed with partial success.",
        )


# ==========================================================
# Runtime Result
# ==========================================================

@dataclass(slots=True)
class ExecutionResult:
    """
    Runtime execution result.
    """

    task: Task
    outcome: Outcome
    success: bool
    started_at: datetime
    finished_at: datetime
    duration: float


# ==========================================================
# Executor
# ==========================================================

class Executor:
    """
    Executes planner decisions.
    """

    def __init__(
        self,
        backend: ExecutionBackend | None = None,
    ) -> None:
        self._backend = backend or RuleBasedExecutor()

    @property
    def backend(self) -> ExecutionBackend:
        return self._backend

    # --------------------------------------------------
    # Main execution API
    # --------------------------------------------------

    def execute(
        self,
        task: Task,
        decision: Decision | None = None,
    ) -> Outcome | ExecutionResult:
        """
        Supports two APIs.

        execute(task, decision) -> Outcome

        execute(task) -> ExecutionResult
        """

        if decision is not None:
            return self._backend.execute(
                task,
                decision,
            )

        # Runtime mode

        decision = Decision(
            description="Compare total trip cost",
            rationale="Default execution path.",
            alternatives=[],
        )

        start = perf_counter()
        started_at = datetime.now(UTC)

        outcome = self._backend.execute(
            task,
            decision,
        )

        finished_at = datetime.now(UTC)
        duration = perf_counter() - start

        return ExecutionResult(
            task=task,
            outcome=outcome,
            success=outcome.status == OutcomeStatus.SUCCESS,
            started_at=started_at,
            finished_at=finished_at,
            duration=duration,
        )

    # --------------------------------------------------
    # Simulation
    # --------------------------------------------------

    def simulate(
        self,
        task: Task,
    ) -> ExecutionResult:
        """
        Simulation currently behaves exactly like execution.
        """

        result = self.execute(task)

        assert isinstance(result, ExecutionResult)

        return result

    # --------------------------------------------------
    # Debugging
    # --------------------------------------------------

    def explain(self) -> dict[str, object]:
        return {
            "executor": type(self).__name__,
            "backend": type(self._backend).__name__,
            "version": "gen1",
        }

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def reset(self) -> None:
        """
        Reserved for future stateful executors.
        """
        return None