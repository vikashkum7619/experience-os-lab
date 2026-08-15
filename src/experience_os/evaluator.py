from __future__ import annotations

from experience_os.models import Decision, Outcome, OutcomeStatus, Task


class DeterministicEvaluator:
    """
    Evaluates planner decisions against a controlled task environment.

    This evaluator is intentionally deterministic for Gen1 so that
    experience can be tested independently of LLM variability.
    """

    def evaluate(self, task: Task, decision: Decision) -> Outcome:
        """Evaluate a decision and return its outcome."""

        traveler_type = task.context.get("traveler_type")

        if traveler_type == "family":
            return self._evaluate_family_task(decision)

        return self._evaluate_general_task(task, decision)

    def _evaluate_family_task(self, decision: Decision) -> Outcome:
        """Evaluate decisions for family travel."""

        if decision.description == "Compare total trip cost":
            return Outcome(
                status=OutcomeStatus.SUCCESS,
                score=1.0,
                metrics={
                    "decision_quality": 1.0,
                    "efficiency": 1.0,
                },
                description=(
                    "The decision accounts for total trip cost, "
                    "including costs that may not appear in the ticket price."
                ),
            )

        return Outcome(
            status=OutcomeStatus.FAILURE,
            score=0.0,
            metrics={
                "decision_quality": 0.0,
                "efficiency": 1.0,
            },
            description=(
                "The decision does not account for the total cost "
                "required for the family trip."
            ),
        )

    def _evaluate_general_task(
        self,
        task: Task,
        decision: Decision,
    ) -> Outcome:
        """Evaluate decisions for non-family tasks."""

        if decision.description == "Compare available options against task constraints":
            return Outcome(
                status=OutcomeStatus.SUCCESS,
                score=0.8,
                metrics={
                    "decision_quality": 0.8,
                    "efficiency": 1.0,
                },
                description=(
                    "The decision explicitly considers the constraints "
                    "provided by the task."
                ),
            )

        return Outcome(
            status=OutcomeStatus.PARTIAL,
            score=0.5,
            metrics={
                "decision_quality": 0.5,
                "efficiency": 1.0,
            },
            description=(
                "The decision may produce a usable result but does not "
                "explicitly demonstrate constraint-based comparison."
            ),
        )