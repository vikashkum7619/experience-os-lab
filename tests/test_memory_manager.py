from __future__ import annotations

from experience_os.consolidation import ExperienceConsolidator
from experience_os.embeddings import DummyEmbeddingProvider
from experience_os.memory_manager import MemoryManager
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)
from experience_os.recall import ExperienceRecall
from experience_os.reflection import ReflectionEngine
from experience_os.semantic_index import SemanticIndex
from experience_os.semantic_recall import SemanticRecall
from experience_os.sqlite_store import SQLiteExperienceStore


def build_manager() -> MemoryManager:
    store = SQLiteExperienceStore(":memory:")

    embeddings = DummyEmbeddingProvider()

    index = SemanticIndex(
        embedding_provider=embeddings,
    )

    symbolic = ExperienceRecall(store)

    recall = SemanticRecall(
        symbolic_recall=symbolic,
        semantic_index=index,
    )

    consolidator = ExperienceConsolidator(
        store=store,
    )

    reflection = ReflectionEngine()

    return MemoryManager(
        store=store,
        recall=recall,
        consolidator=consolidator,
        reflection_engine=reflection,
        semantic_index=index,
    )


def build_experience() -> Experience:
    return Experience(
        conditions={
            "traveler": "family",
        },
        decision_pattern=[
            "check baggage",
            "compare total cost",
        ],
        execution_count=10,
        successful_executions=9,
        confidence=0.90,
    )


def build_task() -> Task:
    return Task(
        goal="Book international flight",
        context={
            "traveler": "family",
        },
    )


def build_decision() -> Decision:
    return Decision(
        description="Compare total cost",
        rationale="Cheapest overall",
    )


def build_outcome() -> Outcome:
    return Outcome(
        status=OutcomeStatus.SUCCESS,
        score=0.95,
        description="Flight booked",
    )


def test_save_stores_experience() -> None:
    manager = build_manager()

    experience = build_experience()

    manager.save(experience)

    stored = manager.all()

    assert len(stored) == 1
    assert stored[0].execution_count == 10


def test_duplicate_is_consolidated() -> None:
    manager = build_manager()

    manager.save(build_experience())
    manager.save(build_experience())

    stored = manager.all()

    assert len(stored) == 1
    assert stored[0].execution_count == 20
    assert stored[0].successful_executions == 18


def test_recall_returns_results() -> None:
    manager = build_manager()

    manager.save(build_experience())

    results = manager.recall(
        build_task(),
    )

    assert len(results) >= 1


def test_reflection_returns_result() -> None:
    manager = build_manager()

    reflection = manager.reflect(
        task=build_task(),
        decision=build_decision(),
        outcome=build_outcome(),
    )

    assert reflection.confidence == 0.95
    assert "successfully" in reflection.summary.lower()


def test_learn_returns_reflection_and_saves() -> None:
    manager = build_manager()

    reflection = manager.learn(
        experience=build_experience(),
        task=build_task(),
        decision=build_decision(),
        outcome=build_outcome(),
    )

    assert reflection.confidence == 0.95
    assert len(manager.all()) == 1