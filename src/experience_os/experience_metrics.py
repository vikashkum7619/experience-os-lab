from __future__ import annotations

from dataclasses import dataclass

from experience_os.models import (
    Experience,
    Outcome,
    OutcomeStatus,
)


@dataclass(frozen=True, slots=True)
class ExperienceMetrics:
    """
    Metrics calculated for a single experience.

    Gen-1
    -----
    Pure rule-based metrics.

    Future generations may include:

    - Semantic similarity
    - Embedding quality
    - Reflection score
    - Knowledge graph centrality
    - Business impact
    """

    success_rate: float
    failure_rate: float
    confidence: float
    execution_count: int
    successful_executions: int
    failed_executions: int


class ExperienceMetricsCalculator:
    """
    Computes metrics for experiences.

    Responsibilities
    ----------------
    - Success rate
    - Failure rate
    - Confidence
    - Execution statistics

    Does NOT
    --------
    - Learn
    - Rank
    - Store
    """

    def calculate(
        self,
        experience: Experience,
    ) -> ExperienceMetrics:
        """
        Compute metrics for one experience.
        """

        execution_count = experience.execution_count
        successful = experience.successful_executions
        failed = max(
            execution_count - successful,
            0,
        )

        if execution_count == 0:
            success_rate = 0.0
            failure_rate = 0.0
        else:
            success_rate = successful / execution_count
            failure_rate = failed / execution_count

        return ExperienceMetrics(
            success_rate=success_rate,
            failure_rate=failure_rate,
            confidence=experience.confidence,
            execution_count=execution_count,
            successful_executions=successful,
            failed_executions=failed,
        )

    def update(
        self,
        experience: Experience,
        outcome: Outcome,
    ) -> ExperienceMetrics:
        """
        Update an experience using a new execution outcome.

        Returns
        -------
        Updated metrics.
        """

        experience.execution_count += 1

        if outcome.status == OutcomeStatus.SUCCESS:
            experience.successful_executions += 1

        experience.confidence = outcome.score

        return self.calculate(experience)

    def success_rate(
        self,
        experience: Experience,
    ) -> float:
        """Return success rate."""

        return self.calculate(
            experience,
        ).success_rate

    def failure_rate(
        self,
        experience: Experience,
    ) -> float:
        """Return failure rate."""

        return self.calculate(
            experience,
        ).failure_rate

    def confidence(
        self,
        experience: Experience,
    ) -> float:
        """Return confidence."""

        return experience.confidence

    def executions(
        self,
        experience: Experience,
    ) -> int:
        """Return execution count."""

        return experience.execution_count

    def successes(
        self,
        experience: Experience,
    ) -> int:
        """Return successful executions."""

        return experience.successful_executions

    def failures(
        self,
        experience: Experience,
    ) -> int:
        """Return failed executions."""

        return max(
            experience.execution_count
            - experience.successful_executions,
            0,
        )

    def is_reliable(
        self,
        experience: Experience,
        minimum_success_rate: float = 0.80,
        minimum_executions: int = 5,
    ) -> bool:
        """
        Determine whether an experience is reliable.

        Default thresholds

        - ≥80% success
        - ≥5 executions
        """

        metrics = self.calculate(
            experience,
        )

        return (
            metrics.execution_count >= minimum_executions
            and metrics.success_rate >= minimum_success_rate
        )