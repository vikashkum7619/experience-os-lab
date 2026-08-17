from __future__ import annotations

from experience_os.episode import Episode
from experience_os.episode_store import EpisodeStore
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
            recommendation="Reuse this strategy.",
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


def test_save_episode() -> None:
    store = EpisodeStore(":memory:")

    episode = build_episode()

    store.save(episode)

    assert store.count() == 1


def test_load_all_episodes() -> None:
    store = EpisodeStore(":memory:")

    episode = build_episode()

    store.save(episode)

    episodes = store.all()

    assert len(episodes) == 1
    assert episodes[0].task.goal == "Book flight"


def test_delete_episode() -> None:
    store = EpisodeStore(":memory:")

    episode = build_episode()

    store.save(episode)

    store.delete(episode.id)

    assert store.count() == 0


def test_clear_store() -> None:
    store = EpisodeStore(":memory:")

    store.save(build_episode())
    store.save(build_episode())

    assert store.count() == 2

    store.clear()

    assert store.count() == 0


def test_count() -> None:
    store = EpisodeStore(":memory:")

    assert store.count() == 0

    store.save(build_episode())

    assert store.count() == 1


def test_save_replaces_existing_episode() -> None:
    store = EpisodeStore(":memory:")

    episode = build_episode()

    store.save(episode)
    store.save(episode)

    assert store.count() == 1


def test_context_manager() -> None:
    with EpisodeStore(":memory:") as store:
        store.save(build_episode())

        assert store.count() == 1