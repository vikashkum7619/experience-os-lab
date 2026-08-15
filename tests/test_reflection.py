from experience_os.models import (
    Decision,
    Outcome,
    OutcomeStatus,
    Task,
)
from experience_os.reflection import ReflectionEngine


def test_success_reflection() -> None:
    engine = ReflectionEngine()

    reflection = engine.reflect(
        task=Task(goal="Book flight"),
        decision=Decision(
            description="Compare total cost",
            rationale="Cheapest overall",
        ),
        outcome=Outcome(
            status=OutcomeStatus.SUCCESS,
            score=0.95,
            description="Booked",
        ),
    )

    assert "successfully" in reflection.summary.lower()
    assert reflection.confidence == 0.95


def test_failure_reflection() -> None:
    engine = ReflectionEngine()

    reflection = engine.reflect(
        task=Task(goal="Book flight"),
        decision=Decision(
            description="Choose cheapest ticket",
            rationale="Lowest fare",
        ),
        outcome=Outcome(
            status=OutcomeStatus.FAILURE,
            score=0.2,
            description="Booking failed",
        ),
    )

    assert "did not achieve" in reflection.summary.lower()
    assert reflection.confidence == 0.8


def test_partial_reflection() -> None:
    engine = ReflectionEngine()

    reflection = engine.reflect(
        task=Task(goal="Book flight"),
        decision=Decision(
            description="Use airline rewards",
            rationale="Reduce cost",
        ),
        outcome=Outcome(
            status=OutcomeStatus.PARTIAL,
            score=0.6,
            description="Partial success",
        ),
    )

    assert "partially" in reflection.summary.lower()
    assert reflection.confidence == 0.6