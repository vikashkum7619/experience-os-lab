from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from experience_os.memory import ExperienceMemory
from experience_os.models import (
    Experience,
    Task,
)
from experience_os.planner import (
    ExperienceInformedPlanner,
    PlannerResult,
)
from experience_os.recall import ExperienceRecall


@dataclass(slots=True)
class PlannerRuntimeResult:
    """
    Result returned by PlannerRuntime.
    """

    task: Task
    result: PlannerResult
    selected_experience: Experience | None
    candidate_experiences: list[Experience] = field(default_factory=list)
    planned_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )


class PlannerRuntime:
    """
    Runtime orchestration layer for planning.

    Gen-1:
        Rule-based recall
        Planner
        Experience reuse
    """

    def __init__(
        self,
        memory: ExperienceMemory | None = None,
    ) -> None:

        self._memory = memory or ExperienceMemory()

        recall = ExperienceRecall(
            self._memory.store,
        )

        self._planner = ExperienceInformedPlanner(
            recall=recall,
        )

    @property
    def memory(self) -> ExperienceMemory:
        return self._memory

    @property
    def planner(self) -> ExperienceInformedPlanner:
        return self._planner

    def plan(
        self,
        task: Task,
    ) -> PlannerRuntimeResult:

        candidates = self._memory.retrieve(task)

        best = candidates[0] if candidates else None

        result = self._planner.plan(task)

        return PlannerRuntimeResult(
            task=task,
            result=result,
            selected_experience=best,
            candidate_experiences=candidates,
        )

    def best_experience(
        self,
        task: Task,
    ) -> Experience | None:

        return self._memory.best(task)

    def candidate_experiences(
        self,
        task: Task,
    ) -> list[Experience]:

        return self._memory.retrieve(task)

    def has_experience(
        self,
        task: Task,
    ) -> bool:

        return self.best_experience(task) is not None

    def explain(
        self,
        task: Task,
    ) -> dict[str, object]:

        candidates = self._memory.retrieve(task)

        return {
            "candidate_count": len(candidates),
            "selected_experience": (
                candidates[0].id if candidates else None
            ),
            "planner": type(self._planner).__name__,
            "memory": type(self._memory).__name__,
        }

    def reset(self) -> None:
        """
        Reserved for future runtime caching.
        """
        return None