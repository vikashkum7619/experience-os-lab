from __future__ import annotations

from dataclasses import dataclass

from experience_os.consolidation import ExperienceConsolidator
from experience_os.evaluator import ExperienceEvaluator
from experience_os.learning import ExperienceLearner
from experience_os.lifecycle import ExperienceLifecycle
from experience_os.memory import ExperienceMemory
from experience_os.models import Decision, Experience, Task
from experience_os.planner import ExperienceInformedPlanner
from experience_os.trust import ExperienceEvidence


@dataclass(frozen=True)
class RuntimeResult:
    """
    Complete execution result of Experience OS.
    """

    task: Task
    decision: Decision
    experience: Experience | None
    success: bool
    confidence: float


class ExperienceRuntime:
    """
    Experience OS Runtime.

    Coordinates every component in the learning loop.

        Task
          ↓
      Planner
          ↓
      Decision
          ↓
      Evaluator
          ↓
      Learning
          ↓
      Lifecycle
          ↓
      Consolidation
          ↓
      Memory
    """

    def __init__(
        self,
        planner: ExperienceInformedPlanner,
        evaluator: ExperienceEvaluator,
        learner: ExperienceLearner,
        lifecycle: ExperienceLifecycle,
        consolidator: ExperienceConsolidator,
        memory: ExperienceMemory,
    ) -> None:
        self._planner = planner
        self._evaluator = evaluator
        self._learner = learner
        self._lifecycle = lifecycle
        self._consolidator = consolidator
        self._memory = memory

    def execute(
        self,
        task: Task,
        *,
        success: bool,
    ) -> RuntimeResult:
        """
        Execute one complete Experience OS cycle.
        """

        #########################################################
        # PLAN
        #########################################################

        plan = self._planner.plan(task)

        #########################################################
        # EVALUATE
        #########################################################

        evaluation = self._evaluator.evaluate(
            decision=plan.decision,
            success=success,
        )

        #########################################################
        # LEARN
        #########################################################

        evidence = ExperienceEvidence()

        evidence.record(success)

        learned = self._learner.learn(
            task=task,
            decision=plan.decision,
            evidence=evidence,
        )

        #########################################################
        # LIFECYCLE
        #########################################################

        state = self._lifecycle.refresh(
            learned,
        )

        #########################################################
        # MEMORY
        #########################################################

        self._memory.add(learned)

        #########################################################
        # CONSOLIDATION
        #########################################################

        if self._lifecycle.should_promote(
            learned,
        ):
            self._consolidator.consolidate(
                self._memory,
            )

        #########################################################
        # RESULT
        #########################################################

        del state

        return RuntimeResult(
            task=task,
            decision=plan.decision,
            experience=learned,
            success=evaluation.success,
            confidence=learned.confidence,
        )