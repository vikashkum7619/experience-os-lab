from __future__ import annotations

from experience_os.context_builder import Context
from experience_os.models import Experience, Task
from experience_os.planner_context import (
    PlannerContextBuilder,
)


def build_experience(
    confidence: float = 0.9,
) -> Experience:
    return Experience(
        conditions={
            "traveler": "family",
        },
        decision_pattern=[
            "compare airlines",
            "book direct",
        ],
        execution_count=10,
        successful_executions=9,
        confidence=confidence,
    )


def build_context(
    experiences: list[Experience],
) -> Context:
    return Context(
        task=Task(
            goal="Book flight",
        ),
        experiences=experiences,
        recent_episodes=[],
        notes=[],
    )


def test_build_returns_planner_context() -> None:
    builder = PlannerContextBuilder()

    context = build_context(
        [build_experience()],
    )

    planner = builder.build(
        context,
    )

    assert planner.context == context
    assert planner.total_experiences == 1


def test_average_confidence() -> None:
    builder = PlannerContextBuilder()

    context = build_context(
        [
            build_experience(0.8),
            build_experience(1.0),
        ],
    )

    planner = builder.build(
        context,
    )

    assert planner.average_confidence == 0.9


def test_recommended_patterns() -> None:
    builder = PlannerContextBuilder()

    context = build_context(
        [build_experience()],
    )

    planner = builder.build(
        context,
    )

    assert len(planner.recommended_patterns) == 1

    assert planner.recommended_patterns[0] == [
        "compare airlines",
        "book direct",
    ]


def test_best_pattern() -> None:
    builder = PlannerContextBuilder()

    planner = builder.build(
        build_context(
            [build_experience()],
        )
    )

    assert builder.best_pattern(
        planner,
    ) == [
        "compare airlines",
        "book direct",
    ]


def test_best_pattern_returns_none() -> None:
    builder = PlannerContextBuilder()

    planner = builder.build(
        build_context([]),
    )

    assert builder.best_pattern(
        planner,
    ) is None


def test_has_experience_true() -> None:
    builder = PlannerContextBuilder()

    planner = builder.build(
        build_context(
            [build_experience()],
        )
    )

    assert builder.has_experience(
        planner,
    )


def test_has_experience_false() -> None:
    builder = PlannerContextBuilder()

    planner = builder.build(
        build_context([]),
    )

    assert not builder.has_experience(
        planner,
    )


def test_empty_context_statistics() -> None:
    builder = PlannerContextBuilder()

    planner = builder.build(
        build_context([]),
    )

    assert planner.total_experiences == 0
    assert planner.average_confidence == 0.0
    assert planner.recommended_patterns == []