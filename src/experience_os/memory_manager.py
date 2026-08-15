from __future__ import annotations

from experience_os.consolidation import ExperienceConsolidator
from experience_os.memory_stats import MemoryStats
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    Task,
)
from experience_os.reflection import (
    Reflection,
    ReflectionEngine,
)
from experience_os.semantic_index import SemanticIndex
from experience_os.semantic_recall import SemanticRecall
from experience_os.sqlite_store import SQLiteExperienceStore


class MemoryManager:
    """
    Central orchestration layer for Experience OS.

    Every interaction with memory should go through this class.
    """

    def __init__(
        self,
        *,
        store: SQLiteExperienceStore,
        recall: SemanticRecall,
        consolidator: ExperienceConsolidator,
        reflection_engine: ReflectionEngine,
        semantic_index: SemanticIndex,
    ) -> None:

        self._store = store
        self._recall = recall
        self._consolidator = consolidator
        self._reflection = reflection_engine
        self._semantic_index = semantic_index

    # -------------------------------------------------------
    # Storage
    # -------------------------------------------------------

    def save(
        self,
        experience: Experience,
    ) -> Experience:

        stored = self._consolidator.consolidate(
            experience,
        )

        self._store.save(stored)

        self._semantic_index.add(stored)

        return stored

    def all(self) -> list[Experience]:
        return self._store.all()

    def clear(self) -> None:
        self._store.clear()

    # -------------------------------------------------------
    # Recall
    # -------------------------------------------------------

    def recall(
        self,
        task: Task,
        *,
        top_k: int = 5,
    ) -> list[Experience]:

        return self._recall.recall(
            task,
            top_k=top_k,
        )

    # -------------------------------------------------------
    # Reflection
    # -------------------------------------------------------

    def reflect(
        self,
        *,
        task: Task,
        decision: Decision,
        outcome: Outcome,
    ) -> Reflection:

        return self._reflection.reflect(
            task=task,
            decision=decision,
            outcome=outcome,
        )

    # -------------------------------------------------------
    # Learning
    # -------------------------------------------------------

    def learn(
        self,
        *,
        experience: Experience,
        task: Task,
        decision: Decision,
        outcome: Outcome,
    ) -> Reflection:

        reflection = self.reflect(
            task=task,
            decision=decision,
            outcome=outcome,
        )

        self.save(experience)

        return reflection

    # -------------------------------------------------------
    # Semantic Index
    # -------------------------------------------------------

    def rebuild_index(self) -> None:

        self._semantic_index.clear()

        for experience in self.all():
            self._semantic_index.add(experience)

    # -------------------------------------------------------
    # Statistics
    # -------------------------------------------------------

    def stats(self) -> MemoryStats:

        experiences = self.all()

        if not experiences:
            return MemoryStats(
                total_experiences=0,
                average_confidence=0.0,
                average_success_rate=0.0,
            )

        avg_confidence = (
            sum(e.confidence for e in experiences)
            / len(experiences)
        )

        avg_success = (
            sum(e.success_rate for e in experiences)
            / len(experiences)
        )

        return MemoryStats(
            total_experiences=len(experiences),
            average_confidence=avg_confidence,
            average_success_rate=avg_success,
        )