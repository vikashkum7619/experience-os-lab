from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)


def test_task_can_be_created() -> None:
    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
        constraints={"max_budget": 80000},
    )

    assert task.goal == "Book an international flight"
    assert task.context["traveler_type"] == "family"
    assert task.constraints["max_budget"] == 80000
    assert task.id is not None
    assert task.created_at.tzinfo is not None


def test_task_rejects_empty_goal() -> None:
    with pytest.raises(ValidationError):
        Task(goal="")


def test_decision_can_be_created() -> None:
    decision = Decision(
        description="Compare total trip cost",
        rationale="Ticket price alone may hide baggage costs",
        alternatives=["ticket_price_only", "total_trip_cost"],
    )

    assert decision.description == "Compare total trip cost"
    assert len(decision.alternatives) == 2


def test_outcome_success() -> None:
    outcome = Outcome(
        status=OutcomeStatus.SUCCESS,
        score=0.95,
        metrics={"cost": 58000.0, "steps": 4.0},
        description="Flight successfully selected",
    )

    assert outcome.status == OutcomeStatus.SUCCESS
    assert outcome.score == 0.95
    assert outcome.metrics["cost"] == 58000.0


def test_outcome_score_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValidationError):
        Outcome(
            status=OutcomeStatus.SUCCESS,
            score=1.5,
            description="Invalid outcome",
        )


def test_experience_success_rate() -> None:
    experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=[
            "check_baggage",
            "check_refundability",
            "compare_total_cost",
        ],
        execution_count=10,
        successful_executions=9,
        confidence=0.9,
    )

    assert experience.success_rate == 0.9


def test_empty_experience_has_zero_success_rate() -> None:
    experience = Experience(
        decision_pattern=["check_total_cost"],
    )

    assert experience.success_rate == 0.0


def test_experience_rejects_empty_decision_pattern() -> None:
    with pytest.raises(ValidationError):
        Experience(decision_pattern=[])


def test_timestamps_are_timezone_aware() -> None:
    task = Task(goal="Test task")

    assert task.created_at.tzinfo is not None
    assert task.created_at.utcoffset() is not None

    
    now = datetime.now(UTC)

    assert task.created_at <= now