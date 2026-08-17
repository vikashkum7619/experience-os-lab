from __future__ import annotations

from dataclasses import dataclass

from experience_os.memory_manager import MemoryManager
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)
from experience_os.planner import ExperienceInformedPlanner
from experience_os.reflection import (
    Reflection,
    ReflectionEngine,
)


@dataclass(slots=True)
class PipelineResult:
    """
    Result of one complete execution.
    """

    task: Task
    decision: Decision
    outcome: Outcome
    reflection: Reflection
    experience: Experience


class ExperiencePipeline:
    """
    Executes one complete Experience OS learning cycle.

    Pipeline
    --------
        Task
          │
          ▼
      Planner
          │
          ▼
      Decision
          │
          ▼
    Reflection Engine
          │
          ▼
      Experience
          │
          ▼
    Memory Manager
    """

    def __init__(
        self,
        *,
        planner: ExperienceInformedPlanner,
        reflection_engine: ReflectionEngine,
        memory: MemoryManager,
    ) -> None:

        self._planner = planner
        self._reflection = reflection_engine
        self._memory = memory

    def run(
        self,
        *,
        task: Task,
        outcome: Outcome,
    ) -> PipelineResult:
        """
        Execute one complete learning cycle.
        """

        # -------------------------------------------------
        # Planning
        # -------------------------------------------------

        planner_result = self._planner.plan(task)
        decision = planner_result.decision

        # -------------------------------------------------
        # Reflection
        # -------------------------------------------------

        reflection = self._reflection.reflect(
            task=task,
            decision=decision,
            outcome=outcome,
        )

        # -------------------------------------------------
        # Experience
        # -------------------------------------------------

        if planner_result.used_experience is not None:

            experience = planner_result.used_experience

            experience.execution_count += 1

            if outcome.status is OutcomeStatus.SUCCESS:
                experience.successful_executions += 1

            experience.confidence = reflection.confidence

        else:

            experience = self._create_experience(
                task=task,
                decision=decision,
                outcome=outcome,
                reflection=reflection,
            )

        # -------------------------------------------------
        # Learn
        # -------------------------------------------------

        self._memory.learn(
            experience=experience,
            task=task,
            decision=decision,
            outcome=outcome,
        )

        return PipelineResult(
            task=task,
            decision=decision,
            outcome=outcome,
            reflection=reflection,
            experience=experience,
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _create_experience(
        *,
        task: Task,
        decision: Decision,
        outcome: Outcome,
        reflection: Reflection,
    ) -> Experience:
        """
        Convert an execution into an Experience.
        """

        return Experience(
            conditions=task.context,
            decision_pattern=[
                decision.description,
            ],
            execution_count=1,
            successful_executions=(
                1
                if outcome.status is OutcomeStatus.SUCCESS
                else 0
            ),
            confidence=reflection.confidence,
        )