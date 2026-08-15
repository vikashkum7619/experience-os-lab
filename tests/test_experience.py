from experience_os.evaluator import DeterministicEvaluator
from experience_os.experience import ExperienceBuilder
from experience_os.models import (
    Decision,
    Outcome,
    OutcomeStatus,
    Task,
)


def test_successful_execution_creates_experience() -> None:
    builder = ExperienceBuilder()

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
        constraints={"max_budget": 80000},
    )

    decision = Decision(
        description="Compare total trip cost",
        rationale="Family travel may include additional costs.",
    )

    outcome = Outcome(
        status=OutcomeStatus.SUCCESS,
        score=1.0,
        description="Successful family travel decision",
    )

    experience = builder.build(task, decision, outcome)

    assert experience is not None
    assert experience.conditions == {"traveler_type": "family"}
    assert experience.decision_pattern == ["Compare total trip cost"]
    assert experience.execution_count == 1
    assert experience.successful_executions == 1
    assert experience.confidence == 1.0


def test_failed_execution_does_not_create_experience() -> None:
    builder = ExperienceBuilder()

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
    )

    decision = Decision(
        description="Select the cheapest ticket",
        rationale="Choose the lowest advertised price.",
    )

    outcome = Outcome(
        status=OutcomeStatus.FAILURE,
        score=0.0,
        description="Decision failed",
    )

    experience = builder.build(task, decision, outcome)

    assert experience is None


def test_partial_execution_does_not_create_experience() -> None:
    builder = ExperienceBuilder()

    task = Task(
        goal="Book a business flight",
        context={"traveler_type": "business"},
    )

    decision = Decision(
        description="Choose the first available option",
        rationale="Use the first option.",
    )

    outcome = Outcome(
        status=OutcomeStatus.PARTIAL,
        score=0.5,
        description="Partially successful decision",
    )

    experience = builder.build(task, decision, outcome)

    assert experience is None


def test_experience_builder_integrates_with_evaluator() -> None:
    evaluator = DeterministicEvaluator()
    builder = ExperienceBuilder()

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
        constraints={"max_budget": 80000},
    )

    decision = Decision(
        description="Compare total trip cost",
        rationale="Family travel may include additional costs.",
    )

    outcome = evaluator.evaluate(task, decision)

    experience = builder.build(task, decision, outcome)

    assert experience is not None
    assert experience.success_rate == 1.0
    assert experience.conditions["traveler_type"] == "family"

def test_experience_preserves_trip_type() -> None:
    builder = ExperienceBuilder()

    task = Task(
        goal="Book an international family flight",
        context={
            "traveler_type": "family",
            "checked_baggage": True,
            "trip_type": "international",
        },
    )

    decision = Decision(
        description="Check baggage before comparing price",
        rationale="Baggage affects total trip cost.",
    )

    outcome = Outcome(
        status=OutcomeStatus.SUCCESS,
        score=1.0,
        metrics={"cost": 65000.0},
        description="Successful flight selection",
    )

    experience = builder.build(
        task,
        decision,
        outcome,
    )

    assert experience is not None
    assert experience.conditions["traveler_type"] == "family"
    assert experience.conditions["checked_baggage"] is True
    assert experience.conditions["trip_type"] == "international"