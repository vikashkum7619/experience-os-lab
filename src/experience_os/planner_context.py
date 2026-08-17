from __future__ import annotations

from dataclasses import dataclass

from experience_os.context_builder import Context
from experience_os.models import Experience


@dataclass(slots=True)
class PlannerContext:
    """
    Rich context supplied to a planner or LLM.

    This extends the generic Context produced by ContextBuilder
    with planning-oriented summaries.
    """

    context: Context
    recommended_patterns: list[list[str]]
    average_confidence: float
    total_experiences: int


class PlannerContextBuilder:
    """
    Converts a generic Context into a planner-ready context.

    Responsibilities
    ----------------
    - Summarize recalled experiences
    - Extract reusable decision patterns
    - Compute confidence statistics
    """

    def build(
        self,
        context: Context,
    ) -> PlannerContext:

        experiences = context.experiences

        recommended_patterns = [
            experience.decision_pattern
            for experience in experiences
        ]

        average_confidence = self._average_confidence(
            experiences,
        )

        return PlannerContext(
            context=context,
            recommended_patterns=recommended_patterns,
            average_confidence=average_confidence,
            total_experiences=len(experiences),
        )

    @staticmethod
    def _average_confidence(
        experiences: list[Experience],
    ) -> float:

        if not experiences:
            return 0.0

        return (
            sum(
                experience.confidence
                for experience in experiences
            )
            / len(experiences)
        )

    def best_pattern(
        self,
        planner_context: PlannerContext,
    ) -> list[str] | None:
        """
        Return the highest-ranked decision pattern.
        """

        if not planner_context.recommended_patterns:
            return None

        return planner_context.recommended_patterns[0]

    def has_experience(
        self,
        planner_context: PlannerContext,
    ) -> bool:
        """
        True if relevant experiences were found.
        """

        return planner_context.total_experiences > 0