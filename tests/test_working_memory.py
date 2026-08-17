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
from experience_os.working_memory import WorkingMemory


def build_experience() -> Experience:
    return Experience(
        conditions={
            "traveler": "family",
        },
        decision_pattern=[
            "compare airlines",
            "book direct flight",
        ],
        execution_count=10,
        successful_executions=9,
        confidence=0.90,
    )


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
            recommendation="Reuse this strategy.",
            confidence=0.95,
        ),
        experience=build_experience(),
    )


def test_new_working_memory_is_empty() -> None:
    memory = WorkingMemory()

    assert memory.empty()
    assert memory.episode_count == 0
    assert memory.experience_count == 0
    assert memory.note_count == 0


def test_add_episode() -> None:
    memory = WorkingMemory()

    episode = build_episode()

    memory.add_episode(episode)

    assert memory.episode_count == 1
    assert memory.latest_episode() == episode


def test_add_experience() -> None:
    memory = WorkingMemory()

    experience = build_experience()

    memory.add_experience(experience)

    assert memory.experience_count == 1
    assert memory.latest_experience() == experience


def test_add_multiple_experiences() -> None:
    memory = WorkingMemory()

    experiences = [
        build_experience(),
        build_experience(),
        build_experience(),
    ]

    memory.add_experiences(experiences)

    assert memory.experience_count == 3


def test_add_note() -> None:
    memory = WorkingMemory()

    memory.add_note("Need to verify baggage policy.")

    assert memory.note_count == 1
    assert memory.notes() == [
        "Need to verify baggage policy."
    ]


def test_empty_note_is_ignored() -> None:
    memory = WorkingMemory()

    memory.add_note("")

    assert memory.note_count == 0


def test_clear() -> None:
    memory = WorkingMemory()

    memory.add_episode(build_episode())
    memory.add_experience(build_experience())
    memory.add_note("temporary")

    memory.clear()

    assert memory.empty()
    assert memory.episode_count == 0
    assert memory.experience_count == 0
    assert memory.note_count == 0


def test_episode_limit() -> None:
    memory = WorkingMemory(
        max_episodes=2,
    )

    memory.add_episode(build_episode())
    memory.add_episode(build_episode())
    memory.add_episode(build_episode())

    assert memory.episode_count == 2


def test_experience_limit() -> None:
    memory = WorkingMemory(
        max_experiences=2,
    )

    memory.add_experience(build_experience())
    memory.add_experience(build_experience())
    memory.add_experience(build_experience())

    assert memory.experience_count == 2


def test_lists_return_copy() -> None:
    memory = WorkingMemory()

    memory.add_episode(build_episode())

    episodes = memory.episodes()

    episodes.clear()

    assert memory.episode_count == 1