from __future__ import annotations

from experience_os.episode import Episode
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)
from experience_os.reflection import Reflection


def build_episode() -> Episode:
    return Episode(
        task=Task(
            goal="Book flight",
        ),
        decision=Decision(
            description="Compare airlines",
            rationale="Lowest total cost",
        ),
        outcome=Outcome(
            status=OutcomeStatus.SUCCESS,
            score=0.95,
            description="Flight booked",
        ),
        reflection=Reflection(
            summary="Decision worked well.",
            recommendation="Reuse for similar trips.",
            confidence=0.95,
        ),
        experience=Experience(
            conditions={
                "traveler": "family",
            },
            decision_pattern=[
                "compare airlines",
                "check baggage",
            ],
            execution_count=10,
            successful_executions=9,
            confidence=0.90,
        ),
    )


def test_episode_creation() -> None:
    episode = build_episode()

    assert episode.task.goal == "Book flight"
    assert episode.decision.description == "Compare airlines"
    assert episode.outcome.description == "Flight booked"


def test_episode_success_property() -> None:
    episode = build_episode()

    assert episode.success is True


def test_episode_score_property() -> None:
    episode = build_episode()

    assert episode.score == 0.95


def test_episode_confidence_property() -> None:
    episode = build_episode()

    assert episode.confidence == 0.90


def test_episode_has_identifier() -> None:
    episode = build_episode()

    assert episode.id is not None


def test_episode_has_created_timestamp() -> None:
    episode = build_episode()

    assert episode.created_at is not None


def test_episode_contains_reflection() -> None:
    episode = build_episode()

    assert episode.reflection.summary == "Decision worked well."
    assert episode.reflection.confidence == 0.95