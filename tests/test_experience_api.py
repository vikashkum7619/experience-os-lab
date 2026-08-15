from __future__ import annotations

from experience_os.experience_api import (
    ExperienceAPI,
    ExperienceAPIResult,
)
from experience_os.models import (
    Experience,
    OutcomeStatus,
    Task,
)
from experience_os.recall import (
    ExperienceRecall,
    ExperienceStore,
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
) -> Experience:
    return Experience(
        conditions={
            "traveler_type": traveler_type,
        },
        decision_pattern=[
            "Compare total trip cost",
        ],
        execution_count=10,
        successful_executions=10,
        confidence=1.0,
    )


def make_api() -> ExperienceAPI:
    store = ExperienceStore()
    recall = ExperienceRecall(store)
    return ExperienceAPI(recall)


def make_api_with_experience() -> ExperienceAPI:
    store = ExperienceStore()
    store.add(make_experience())
    recall = ExperienceRecall(store)
    return ExperienceAPI(recall)


# ---------------------------------------------------------
# Construction
# ---------------------------------------------------------

def test_api_constructs() -> None:
    api = make_api()

    assert api is not None


def test_api_has_planner() -> None:
    api = make_api()

    assert api.planner is not None


def test_api_has_executor() -> None:
    api = make_api()

    assert api.executor is not None


def test_api_has_validator() -> None:
    api = make_api()

    assert api.validator is not None


def test_api_has_learner() -> None:
    api = make_api()

    assert api.learner is not None


# ---------------------------------------------------------
# Planning
# ---------------------------------------------------------

def test_plan_returns_planner_result() -> None:
    api = make_api()

    result = api.plan(make_task())

    assert result.decision is not None


def test_plan_returns_decision() -> None:
    api = make_api()

    result = api.plan(make_task())

    assert result.decision.description != ""


def test_plan_uses_experience_when_available() -> None:
    api = make_api_with_experience()

    result = api.plan(make_task())

    assert result.used_experience is not None


def test_plan_without_experience_uses_baseline() -> None:
    api = make_api()

    result = api.plan(make_task())

    assert result.used_experience is None


# ---------------------------------------------------------
# Execute Pipeline
# ---------------------------------------------------------

def test_execute_returns_api_result() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert isinstance(result, ExperienceAPIResult)


def test_execute_returns_task() -> None:
    api = make_api()

    task = make_task()

    result = api.execute(task)

    assert result.task == task


def test_execute_returns_planner_result() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert result.planner_result is not None


def test_execute_returns_outcome() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert result.outcome is not None


def test_execute_returns_validation() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert result.validation is not None


def test_execute_returns_successful_outcome() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert result.outcome.status == OutcomeStatus.SUCCESS


# ---------------------------------------------------------
# Learning
# ---------------------------------------------------------

def test_valid_execution_creates_experience() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert result.learned_experience is not None


def test_learned_experience_contains_conditions() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert (
        result.learned_experience.conditions["traveler_type"]
        == "family"
    )


def test_learned_experience_contains_decision() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert (
        len(result.learned_experience.decision_pattern)
        > 0
    )


# ---------------------------------------------------------
# Experience reuse
# ---------------------------------------------------------

def test_execute_with_existing_experience_reuses_it() -> None:
    api = make_api_with_experience()

    result = api.execute(make_task())

    assert result.planner_result.used_experience is not None


def test_reused_experience_matches_condition() -> None:
    api = make_api_with_experience()

    result = api.execute(make_task())

    assert (
        result.planner_result.used_experience.conditions[
            "traveler_type"
        ]
        == "family"
    )


# ---------------------------------------------------------
# Validator
# ---------------------------------------------------------

def test_validation_passes() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert result.validation.valid


def test_validation_score_positive() -> None:
    api = make_api()

    result = api.execute(make_task())

    assert result.validation.score > 0


# ---------------------------------------------------------
# Multiple executions
# ---------------------------------------------------------

def test_multiple_executions() -> None:
    api = make_api()

    for _ in range(5):
        result = api.execute(make_task())
        assert result.outcome.status == OutcomeStatus.SUCCESS


def test_multiple_tasks() -> None:
    api = make_api()

    api.execute(make_task("family"))
    api.execute(make_task("business"))
    api.execute(make_task("family"))


def test_execute_returns_new_result_each_time() -> None:
    api = make_api()

    result1 = api.execute(make_task())
    result2 = api.execute(make_task())

    assert result1 is not result2