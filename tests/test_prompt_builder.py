from __future__ import annotations

from experience_os.context_builder import Context
from experience_os.episode import Episode
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)
from experience_os.planner_context import PlannerContext
from experience_os.prompt_builder import PromptBuilder
from experience_os.reflection import Reflection


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------


def build_task() -> Task:
    return Task(
        goal="Book a family vacation",
        context={
            "destination": "Japan",
        },
        constraints={
            "budget": "2000 USD",
        },
    )


def build_experience() -> Experience:
    return Experience(
        conditions={
            "traveler": "family",
        },
        decision_pattern=[
            "Compare airlines",
            "Book direct flight",
        ],
        execution_count=10,
        successful_executions=9,
        confidence=0.90,
    )


def build_episode() -> Episode:
    return Episode(
        task=build_task(),
        decision=Decision(
            description="Book flight",
            rationale="Lowest cost",
            alternatives=[],
        ),
        outcome=Outcome(
            status=OutcomeStatus.SUCCESS,
            score=0.95,
            description="Completed",
        ),
        reflection=Reflection(
            summary="Worked well.",
            recommendation="Reuse this strategy.",
            confidence=0.90,
        ),
        experience=build_experience(),
    )


def build_context() -> Context:
    return Context(
        task=build_task(),
        experiences=[
            build_experience(),
        ],
        recent_episodes=[
            build_episode(),
        ],
        notes=[
            "User prefers window seat.",
            "Carry one checked bag.",
        ],
    )


def build_planner_context() -> PlannerContext:
    return PlannerContext(
        context=build_context(),
        recommended_patterns=[
            [
                "Compare airlines",
                "Book direct flight",
            ]
        ],
        average_confidence=0.90,
        total_experiences=1,
    )


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------


def test_build_returns_string() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert isinstance(prompt, str)


def test_prompt_starts_with_task() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert prompt.startswith("# Task")


def test_contains_task_goal() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "Book a family vacation" in prompt


def test_contains_task_context() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "destination" in prompt
    assert "Japan" in prompt


def test_contains_constraints() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "budget" in prompt
    assert "2000 USD" in prompt


def test_contains_working_memory_heading() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "# Working Memory" in prompt


def test_contains_notes() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "User prefers window seat." in prompt
    assert "Carry one checked bag." in prompt


def test_contains_recent_episodes_heading() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "# Recent Episodes" in prompt


def test_contains_episode_goal() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "Book a family vacation" in prompt


def test_contains_experience_heading() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "# Relevant Experiences" in prompt


def test_contains_average_confidence() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "Average Confidence" in prompt
    assert "0.90" in prompt


def test_contains_decision_pattern() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "Compare airlines" in prompt
    assert "Book direct flight" in prompt


def test_prompt_contains_all_sections() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert "# Task" in prompt
    assert "# Working Memory" in prompt
    assert "# Recent Episodes" in prompt
    assert "# Relevant Experiences" in prompt


def test_prompt_is_not_empty() -> None:
    prompt = PromptBuilder().build(
        build_planner_context(),
    )

    assert prompt.strip() != ""


def test_prompt_contains_experience_count() -> None:
    planner_context = build_planner_context()

    assert planner_context.total_experiences == 1
    assert planner_context.average_confidence == 0.90