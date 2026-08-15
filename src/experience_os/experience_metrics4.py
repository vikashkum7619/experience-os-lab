from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExperienceMetrics:
    """
    Runtime metrics for Experience OS.

    Responsibilities
    ----------------
    - Count runtime operations.
    - Measure execution quality.
    - Report system health.

    Does NOT
    --------
    - Store experiences
    - Plan
    - Execute
    - Learn
    - Validate

    Gen-1
    -----
    In-memory counters.

    Gen-2+
    ------
    Can later export metrics to Prometheus,
    OpenTelemetry, Grafana, CloudWatch, etc.
    """

    total_tasks: int = 0

    planner_calls: int = 0

    executor_calls: int = 0

    validator_calls: int = 0

    learning_updates: int = 0

    successful_executions: int = 0

    failed_executions: int = 0

    reused_experiences: int = 0

    new_experiences: int = 0

    total_score: float = 0.0

    # --------------------------------------------------
    # Recording
    # --------------------------------------------------

    def record_task(self) -> None:
        self.total_tasks += 1

    def record_planner(self) -> None:
        self.planner_calls += 1

    def record_executor(self) -> None:
        self.executor_calls += 1

    def record_validator(self) -> None:
        self.validator_calls += 1

    def record_learning(self) -> None:
        self.learning_updates += 1

    def record_success(
        self,
        score: float,
    ) -> None:
        self.successful_executions += 1
        self.total_score += score

    def record_failure(
        self,
        score: float = 0.0,
    ) -> None:
        self.failed_executions += 1
        self.total_score += score

    def record_reused_experience(self) -> None:
        self.reused_experiences += 1

    def record_new_experience(self) -> None:
        self.new_experiences += 1

    # --------------------------------------------------
    # Derived Metrics
    # --------------------------------------------------

    @property
    def total_executions(self) -> int:
        return (
            self.successful_executions
            + self.failed_executions
        )

    @property
    def success_rate(self) -> float:
        total = self.total_executions

        if total == 0:
            return 0.0

        return self.successful_executions / total

    @property
    def failure_rate(self) -> float:
        total = self.total_executions

        if total == 0:
            return 0.0

        return self.failed_executions / total

    @property
    def average_score(self) -> float:
        total = self.total_executions

        if total == 0:
            return 0.0

        return self.total_score / total

    @property
    def reuse_rate(self) -> float:
        total = (
            self.reused_experiences
            + self.new_experiences
        )

        if total == 0:
            return 0.0

        return self.reused_experiences / total

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def snapshot(self) -> dict[str, float | int]:
        """
        Return a metrics snapshot.
        """

        return {
            "total_tasks": self.total_tasks,
            "planner_calls": self.planner_calls,
            "executor_calls": self.executor_calls,
            "validator_calls": self.validator_calls,
            "learning_updates": self.learning_updates,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "reused_experiences": self.reused_experiences,
            "new_experiences": self.new_experiences,
            "total_executions": self.total_executions,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "average_score": self.average_score,
            "reuse_rate": self.reuse_rate,
        }

    def reset(self) -> None:
        """
        Reset all metrics.
        """

        self.total_tasks = 0
        self.planner_calls = 0
        self.executor_calls = 0
        self.validator_calls = 0
        self.learning_updates = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.reused_experiences = 0
        self.new_experiences = 0
        self.total_score = 0.0