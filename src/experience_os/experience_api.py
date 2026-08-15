from __future__ import annotations

from dataclasses import dataclass

from experience_os.executor import Executor
from experience_os.learning import ExperienceLearner
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    Task,
)
from experience_os.planner import (
    ExperienceInformedPlanner,
    PlannerResult,
)
from experience_os.recall import ExperienceRecall
from experience_os.validator import (
    ValidationResult,
    Validator,
)


@dataclass(slots=True)
class ExperienceAPIResult:
    """
    Result returned by ExperienceAPI.execute().

    Represents the complete output of a single
    Experience OS execution.
    """

    task: Task
    planner_result: PlannerResult
    outcome: Outcome
    validation: ValidationResult
    learned_experience: Experience | None = None


class ExperienceAPI:
    """
    Public API for Experience OS.

    Gen-1 Pipeline

        Task
          │
          ▼
      Experience Planner
          │
          ▼
      Decision
          │
          ▼
      Executor
          │
          ▼
      Outcome
          │
          ▼
      Validator
          │
          ▼
      Learner
          │
          ▼
      Experience

    Future generations (Semantic Memory, Knowledge Graph,
    Reflection Engine, etc.) can replace internal components
    without changing this API.
    """

    def __init__(
        self,
        recall: ExperienceRecall,
        planner: ExperienceInformedPlanner | None = None,
        executor: Executor | None = None,
        validator: Validator | None = None,
        learner: ExperienceLearner | None = None,
    ) -> None:

        self._planner = planner or ExperienceInformedPlanner(
            recall=recall,
        )

        self._executor = executor or Executor()

        self._validator = validator or Validator()

        self._learner = learner or ExperienceLearner()

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def planner(self) -> ExperienceInformedPlanner:
        return self._planner

    @property
    def executor(self) -> Executor:
        return self._executor

    @property
    def validator(self) -> Validator:
        return self._validator

    @property
    def learner(self) -> ExperienceLearner:
        return self._learner

    # ---------------------------------------------------------
    # Planning
    # ---------------------------------------------------------

    def plan(
        self,
        task: Task,
    ) -> PlannerResult:
        """
        Generate a planning decision.
        """
        return self._planner.plan(task)

    # ---------------------------------------------------------
    # Execution Pipeline
    # ---------------------------------------------------------

    def execute(
        self,
        task: Task,
    ) -> ExperienceAPIResult:
        """
        Execute the complete Experience OS pipeline.
        """

        # -----------------------------
        # Planning
        # -----------------------------
        planner_result = self.plan(task)

        decision: Decision = planner_result.decision

        # -----------------------------
        # Execution
        # -----------------------------
        outcome: Outcome = self._executor.execute(
            task,
            decision,
        )

        # -----------------------------
        # Validation
        # -----------------------------
        validation = self._validator.validate(
            outcome,
        )

        # -----------------------------
        # Learning
        # -----------------------------
        learned_experience: Experience | None = None

        if validation.is_valid:
            learned_experience = self._learner.learn(
                task=task,
                decision=decision,
                outcome=outcome,
            )

        # -----------------------------
        # Return complete result
        # -----------------------------
        return ExperienceAPIResult(
            task=task,
            planner_result=planner_result,
            outcome=outcome,
            validation=validation,
            learned_experience=learned_experience,
        )