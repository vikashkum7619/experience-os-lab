from __future__ import annotations

from experience_os.context_builder import ContextBuilder
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


# ---------------------------------------------------------
# Fake Semantic Recall
# ---------------------------------------------------------

class FakeSemanticRecall:
    """
    Simple fake used for unit testing.
    """

    def __init__(
        self,
        experiences: list[Experience],
    ) -> None:
        self._experiences = experiences

    def recall(
        self,
        task: Task,
        *,
        top_k: int = 5,
    ) -> list[Experience]:
        return self._experiences[:top_k]


# ---------------------------------------------------------
# Builders
# ---------------------------------------------------------

def build_experience() -> Experience:
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
        confidence=0.90,
    )


def build_episode() -> Episode:
    return Episode(
        task=Task(
            goal="Book flight",
        ),
        decision=Decision(
            description="Compare airlines",
            rationale="Cheapest overall",
        ),
        outcome=Outcome(
            status=OutcomeStatus.SUCCESS,
            score=0.95,
            description="Booked",
        ),
        reflection=Reflection(
            summary="Worked well.",
            recommendation="Reuse.",
            confidence=0.95,
        ),
        experience=build_experience(),
    )


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_build_returns_context() -> None:
    experience = build_experience()

    recall = FakeSemanticRecall(
        [experience],
    )

    memory = WorkingMemory()

    builder = ContextBuilder(
        recall=recall,
        working_memory=memory,
    )

    task = Task(
        goal="Book flight",
    )

    context = builder.build(task)

    assert context.task == task
    assert len(context.experiences) == 1


def test_context_contains_recent_episode() -> None:
    episode = build_episode()

    recall = FakeSemanticRecall([])

    memory = WorkingMemory()

    memory.add_episode(episode)

    builder = ContextBuilder(
        recall=recall,
        working_memory=memory,
    )

    context = builder.build(
        Task(goal="Book flight"),
    )

    assert len(context.recent_episodes) == 1

    assert context.recent_episodes[0] == episode


def test_context_contains_notes() -> None:
    recall = FakeSemanticRecall([])

    memory = WorkingMemory()

    memory.add_note(
        "Verify baggage policy.",
    )

    builder = ContextBuilder(
        recall=recall,
        working_memory=memory,
    )

    context = builder.build(
        Task(goal="Book flight"),
    )

    assert context.notes == [
        "Verify baggage policy."
    ]


def test_refresh_returns_new_context() -> None:
    recall = FakeSemanticRecall(
        [build_experience()],
    )

    memory = WorkingMemory()

    builder = ContextBuilder(
        recall=recall,
        working_memory=memory,
    )

    task = Task(
        goal="Book flight",
    )

    context = builder.refresh(task)

    assert context.task == task

    assert len(context.experiences) == 1


def test_top_k_is_respected() -> None:
    experiences = [
        build_experience(),
        build_experience(),
        build_experience(),
    ]

    recall = FakeSemanticRecall(
        experiences,
    )

    builder = ContextBuilder(
        recall=recall,
        working_memory=WorkingMemory(),
    )

    context = builder.build(
        Task(goal="Book flight"),
        top_k=2,
    )

    assert len(context.experiences) == 2


def test_empty_working_memory() -> None:
    builder = ContextBuilder(
        recall=FakeSemanticRecall([]),
        working_memory=WorkingMemory(),
    )

    context = builder.build(
        Task(goal="Book hotel"),
    )

    assert context.recent_episodes == []

    assert context.notes == []

    assert context.experiences == []


def test_multiple_notes_are_returned() -> None:
    memory = WorkingMemory()

    memory.add_note("First")

    memory.add_note("Second")

    builder = ContextBuilder(
        recall=FakeSemanticRecall([]),
        working_memory=memory,
    )

    context = builder.build(
        Task(goal="Travel"),
    )

    assert context.notes == [
        "First",
        "Second",
    ]


def test_multiple_episodes_are_returned() -> None:
    memory = WorkingMemory()

    memory.add_episode(build_episode())

    memory.add_episode(build_episode())

    builder = ContextBuilder(
        recall=FakeSemanticRecall([]),
        working_memory=memory,
    )

    context = builder.build(
        Task(goal="Travel"),
    )

    assert len(
        context.recent_episodes
    ) == 2