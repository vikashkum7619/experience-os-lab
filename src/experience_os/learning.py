from __future__ import annotations

from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    Task,
)
from experience_os.trust import (
    EvidenceAccumulator,
    ExperienceEvidence,
    TrustCalculator,
)


class ExperienceLearner:
    """
    Learns new experiences and updates existing ones.

    Supports two APIs:

    1. learn(task=..., decision=..., outcome=...)
       -> creates a new Experience

    2. learn(experience, success=True/False)
       -> updates an existing Experience
    """

    def __init__(self) -> None:
        self._accumulator = EvidenceAccumulator()
        self._calculator = TrustCalculator()

    def learn(
        self,
        experience: Experience | None = None,
        *,
        success: bool | None = None,
        task: Task | None = None,
        decision: Decision | None = None,
        outcome: Outcome | None = None,
    ) -> Experience:
        """
        Learn from an execution.

        Supports both:
            learn(experience, success=True)

        and

            learn(task=..., decision=..., outcome=...)
        """

        # -------------------------------------------------
        # Update existing experience
        # -------------------------------------------------
        if experience is not None:
            if success is None:
                raise ValueError(
                    "success must be supplied when updating an experience."
                )

            evidence = ExperienceEvidence(
                executions=experience.execution_count,
                successes=experience.successful_executions,
                failures=(
                    experience.execution_count
                    - experience.successful_executions
                ),
            )

            self._accumulator.accumulate(
                evidence,
                success=success,
            )

            experience.execution_count = evidence.executions
            experience.successful_executions = evidence.successes
            experience.confidence = self._calculator.calculate(
                evidence
            )

            return experience

        # -------------------------------------------------
        # Create new experience
        # -------------------------------------------------
        if task is None or decision is None or outcome is None:
            raise ValueError(
                "task, decision and outcome are required "
                "when creating a new experience."
            )

        return Experience(
            conditions=dict(task.context),
            decision_pattern=[
                decision.description,
            ],
            execution_count=1,
            successful_executions=(
                1 if outcome.score > 0 else 0
            ),
            confidence=outcome.score,
        )