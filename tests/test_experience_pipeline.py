from __future__ import annotations

from experience_os.experience_pipeline import ExperiencePipeline
from experience_os.models import (
    Decision,
    Outcome,
    OutcomeStatus,
    Task,
)
from experience_os.planner import PlannerResult
from experience_os.reflection import Reflection


# ---------------------------------------------------------------------
# Fake Components
# ---------------------------------------------------------------------


class FakePlanner:
    def __init__(self) -> None:
        self.called = False

    def plan(self, task: Task) -> PlannerResult:
        self.called = True

        return PlannerResult(
            decision=Decision(
                description="Use cached supplier",
                rationale="Best historical option",
                alternatives=["A", "B"],
            ),
            used_experience=None,
        )


class FakeReflectionEngine:
    def __init__(self) -> None:
        self.called = False

    def reflect(
        self,
        *,
        task,
        decision,
        outcome,
    ) -> Reflection:

        self.called = True

        return Reflection(
            summary="Execution succeeded.",
            recommendation="Reuse this decision.",
            confidence=0.90,
        )


class FakeMemoryManager:
    def __init__(self) -> None:
        self.called = False
        self.last_experience = None

    def learn(
        self,
        *,
        experience,
        task,
        decision,
        outcome,
    ):
        self.called = True
        self.last_experience = experience


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def build_pipeline():

    planner = FakePlanner()
    reflection = FakeReflectionEngine()
    memory = FakeMemoryManager()

    pipeline = ExperiencePipeline(
        planner=planner,
        reflection_engine=reflection,
        memory=memory,
    )

    return pipeline, planner, reflection, memory


def build_task() -> Task:

    return Task(
        goal="Choose supplier",
        context={
            "country": "India",
        },
        constraints={
            "budget": "1000",
        },
    )


def success_outcome() -> Outcome:

    return Outcome(
        status=OutcomeStatus.SUCCESS,
        score=0.95,
        description="Execution completed successfully.",
    )


def failure_outcome() -> Outcome:

    return Outcome(
        status=OutcomeStatus.FAILURE,
        score=0.20,
        description="Execution failed.",
    )


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------


def test_pipeline_initialization():

    pipeline, _, _, _ = build_pipeline()

    assert pipeline is not None


def test_planner_called():

    pipeline, planner, _, _ = build_pipeline()

    pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert planner.called is True


def test_reflection_called():

    pipeline, _, reflection, _ = build_pipeline()

    pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert reflection.called is True


def test_memory_learn_called():

    pipeline, _, _, memory = build_pipeline()

    pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert memory.called is True


def test_pipeline_returns_result():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.task.goal == "Choose supplier"


def test_decision_created():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.decision.description == "Use cached supplier"


def test_reflection_confidence():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.reflection.confidence == 0.90


def test_experience_created():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.experience.execution_count == 1


def test_success_execution_count():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.experience.successful_executions == 1


def test_failure_execution_count():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=failure_outcome(),
    )

    assert result.experience.successful_executions == 0


def test_confidence_propagated():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.experience.confidence == 0.90


def test_decision_pattern_saved():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.experience.decision_pattern == [
        "Use cached supplier",
    ]


def test_conditions_saved():

    pipeline, _, _, _ = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert result.experience.conditions == {
        "country": "India",
    }


def test_memory_receives_same_experience():

    pipeline, _, _, memory = build_pipeline()

    result = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert memory.last_experience is result.experience


def test_multiple_runs_create_new_experiences():

    pipeline, _, _, _ = build_pipeline()

    first = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    second = pipeline.run(
        task=build_task(),
        outcome=success_outcome(),
    )

    assert first.experience.id != second.experience.id