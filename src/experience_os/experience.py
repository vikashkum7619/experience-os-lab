from __future__ import annotations

from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)


class ExperienceBuilder:
    """Build reusable experience from successful task executions."""

    def build(
        self,
        task: Task,
        decision: Decision,
        outcome: Outcome,
    ) -> Experience | None:
        """
        Convert a successful execution into reusable experience.

        Only meaningful task context is retained. This allows the
        resulting experience to distinguish otherwise similar tasks
        such as domestic and international travel.
        """

        if outcome.status != OutcomeStatus.SUCCESS:
            return None

        if outcome.score <= 0.0:
            return None

        conditions: dict[str, object] = {}

        for key in (
            "traveler_type",
            "checked_baggage",
            "trip_type",
        ):
            if key in task.context:
                conditions[key] = task.context[key]

        if not conditions:
            return None

        return Experience(
            conditions=conditions,
            decision_pattern=[decision.description],
            execution_count=1,
            successful_executions=1,
            confidence=outcome.score,
        )