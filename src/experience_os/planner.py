from __future__ import annotations

from dataclasses import dataclass

from experience_os.models import (
    ApplicabilityStatus,
    Decision,
    Experience,
    Task,
)
from experience_os.ranking import ExperienceRanker
from experience_os.recall import (
    ExperienceApplicability,
    ExperienceRecall,
)


@dataclass(frozen=True)
class PlannerResult:
    """Result produced by a planner."""

    decision: Decision
    used_experience: Experience | None = None


class DeterministicPlanner:
    """
    Baseline planner used as the control condition.

    This planner does not access Experience OS.
    """

    def plan(self, task: Task) -> PlannerResult:
        """Create a deterministic decision."""

        traveler_type = task.context.get("traveler_type")

        if traveler_type == "family":
            decision = Decision(
                description="Compare total trip cost",
                rationale=(
                    "Family travel may involve baggage and other costs "
                    "that are not included in the ticket price."
                ),
                alternatives=[
                    "ticket_price_only",
                    "compare_total_trip_cost",
                ],
            )

            return PlannerResult(decision=decision)

        decision = Decision(
            description="Compare available options against task constraints",
            rationale=(
                "Use task constraints to select the most suitable option."
            ),
            alternatives=[
                "first_available_option",
                "constraint_based_comparison",
            ],
        )

        return PlannerResult(decision=decision)


class ExperienceInformedPlanner:
    """
    Planner that safely reuses validated experience.

    Pipeline

        Recall
            ↓
        Applicability
            ↓
        Ranking
            ↓
        Reuse best experience
            ↓
        Otherwise baseline planner
    """

    def __init__(
        self,
        recall: ExperienceRecall,
        baseline: DeterministicPlanner | None = None,
        applicability: ExperienceApplicability | None = None,
        ranker: ExperienceRanker | None = None,
    ) -> None:
        self._recall = recall
        self._baseline = baseline or DeterministicPlanner()
        self._applicability = applicability or ExperienceApplicability()
        self._ranker = ranker or ExperienceRanker()

    def plan(self, task: Task) -> PlannerResult:
        """Plan using validated experience whenever safe."""

        recalled = self._recall.recall(task)

        applicable: list[Experience] = []

        for experience in recalled:
            result = self._applicability.evaluate(
                experience,
                task,
            )

            if result.status == ApplicabilityStatus.APPLY:
                applicable.append(experience)

        if not applicable:
            return self._baseline.plan(task)

        ranked = self._ranker.rank(
            applicable,
            task,
        )

        best = ranked[0].experience

        decision = Decision(
            description=best.decision_pattern[0],
            rationale=(
                "Decision reused from highest-ranked validated experience."
            ),
            alternatives=[
                "reuse_validated_experience",
                "use_baseline_strategy",
            ],
        )

        return PlannerResult(
            decision=decision,
            used_experience=best,
        )