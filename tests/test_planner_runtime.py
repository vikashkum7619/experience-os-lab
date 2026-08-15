from __future__ import annotations

from experience_os.memory import ExperienceMemory
from experience_os.models import (
    Experience,
    Task,
)
from experience_os.planner_runtime import (
    PlannerRuntime,
    PlannerRuntimeResult,
)


def make_task(
    traveler_type: str = "family",
) -> Task:
    return Task(
        goal="Book flight",
        context={
            "traveler_type": traveler_type,
        },
    )


def make_experience(
    traveler_type: str = "family",
    confidence: float = 1.0,
    execution_count: int = 10,
) -> Experience:
    return Experience(
        conditions={
            "traveler_type": traveler_type,
        },
        decision_pattern=[
            "Choose lowest total cost",
        ],
        execution_count=execution_count,
        successful_executions=execution_count,
        confidence=confidence,
    )


def test_runtime_creates_default_dependencies() -> None:
    runtime = PlannerRuntime()

    assert runtime.memory is not None
    assert runtime.planner is not None


def test_plan_returns_runtime_result() -> None:
    runtime = PlannerRuntime()

    result = runtime.plan(
        make_task(),
    )

    assert isinstance(
        result,
        PlannerRuntimeResult,
    )


def test_result_contains_original_task() -> None:
    runtime = PlannerRuntime()

    task = make_task()

    result = runtime.plan(task)

    assert result.task == task


def test_result_contains_planner_result() -> None:
    runtime = PlannerRuntime()

    result = runtime.plan(
        make_task(),
    )

    assert result.result is not None
    assert result.result.decision is not None


def test_result_has_timestamp() -> None:
    runtime = PlannerRuntime()

    result = runtime.plan(
        make_task(),
    )

    assert result.planned_at is not None


def test_best_experience_returns_none_when_memory_empty() -> None:
    runtime = PlannerRuntime()

    assert runtime.best_experience(
        make_task(),
    ) is None


def test_has_experience_returns_false_when_empty() -> None:
    runtime = PlannerRuntime()

    assert not runtime.has_experience(
        make_task(),
    )


def test_candidate_experiences_returns_empty_list() -> None:
    runtime = PlannerRuntime()

    assert runtime.candidate_experiences(
        make_task(),
    ) == []


def test_runtime_uses_memory() -> None:
    memory = ExperienceMemory()

    experience = make_experience()

    memory.store_experience(experience)

    runtime = PlannerRuntime(memory=memory)

    assert runtime.has_experience(
        make_task(),
    )


def test_best_experience_returns_matching_experience() -> None:
    memory = ExperienceMemory()

    experience = make_experience()

    memory.store_experience(experience)

    runtime = PlannerRuntime(memory=memory)

    best = runtime.best_experience(
        make_task(),
    )

    assert best is not None
    assert best.id == experience.id


def test_candidate_experiences_returns_matching_experience() -> None:
    memory = ExperienceMemory()

    experience = make_experience()

    memory.store_experience(experience)

    runtime = PlannerRuntime(memory=memory)

    candidates = runtime.candidate_experiences(
        make_task(),
    )

    assert len(candidates) == 1
    assert candidates[0].id == experience.id


def test_plan_returns_selected_experience() -> None:
    memory = ExperienceMemory()

    experience = make_experience()

    memory.store_experience(experience)

    runtime = PlannerRuntime(memory=memory)

    result = runtime.plan(
        make_task(),
    )

    assert result.selected_experience is not None
    assert result.selected_experience.id == experience.id


def test_plan_returns_candidate_experiences() -> None:
    memory = ExperienceMemory()

    experience = make_experience()

    memory.store_experience(experience)

    runtime = PlannerRuntime(memory=memory)

    result = runtime.plan(
        make_task(),
    )

    assert len(result.candidate_experiences) == 1


def test_explain_returns_dictionary() -> None:
    runtime = PlannerRuntime()

    explanation = runtime.explain(
        make_task(),
    )

    assert isinstance(
        explanation,
        dict,
    )


def test_explain_contains_candidate_count() -> None:
    runtime = PlannerRuntime()

    explanation = runtime.explain(
        make_task(),
    )

    assert "candidate_count" in explanation


def test_explain_contains_selected_experience() -> None:
    runtime = PlannerRuntime()

    explanation = runtime.explain(
        make_task(),
    )

    assert "selected_experience" in explanation


def test_explain_contains_planner_name() -> None:
    runtime = PlannerRuntime()

    explanation = runtime.explain(
        make_task(),
    )

    assert "planner" in explanation


def test_explain_contains_memory_name() -> None:
    runtime = PlannerRuntime()

    explanation = runtime.explain(
        make_task(),
    )

    assert "memory" in explanation


def test_reset_does_not_fail() -> None:
    runtime = PlannerRuntime()

    runtime.reset()


def test_reset_preserves_functionality() -> None:
    runtime = PlannerRuntime()

    runtime.reset()

    result = runtime.plan(
        make_task(),
    )

    assert result.result is not None
    assert result.result.decision is not None