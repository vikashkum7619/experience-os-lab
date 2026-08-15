from __future__ import annotations

from dataclasses import dataclass

from experience_os.models import (
    Decision,
    Outcome,
    OutcomeStatus,
    Task,
)


@dataclass(slots=True)
class Reflection:
    summary: str
    recommendation: str
    confidence: float


class ReflectionEngine:
    """
    Produces execution reflections.
    """

    def reflect(
        self,
        *,
        task: Task,
        decision: Decision,
        outcome: Outcome,
    ) -> Reflection:

        if outcome.status is OutcomeStatus.SUCCESS:
            return Reflection(
                summary=(
                    f"Decision '{decision.description}' "
                    "achieved the task successfully."
                ),
                recommendation=(
                    "Reuse this decision pattern when similar "
                    "conditions are encountered."
                ),
                confidence=outcome.score,
            )

        if outcome.status is OutcomeStatus.PARTIAL:
            return Reflection(
                summary=(
                    f"Decision '{decision.description}' "
                    "partially achieved the objective."
                ),
                recommendation=(
                    "Consider combining this decision with an "
                    "alternative strategy."
                ),
                confidence=outcome.score,
            )

        return Reflection(
            summary=(
                f"Decision '{decision.description}' "
                "did not achieve the desired outcome."
            ),
            recommendation=(
                "Avoid repeating this decision under the same "
                "conditions without modification."
            ),
            confidence=1.0 - outcome.score,
        )