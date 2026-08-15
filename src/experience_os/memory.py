from __future__ import annotations

from uuid import UUID

from experience_os.consolidation import ExperienceConsolidator
from experience_os.experience import ExperienceBuilder
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    Task,
)
from experience_os.ranking import ExperienceRanker
from experience_os.recall import (
    ExperienceApplicability,
    ExperienceRecall,
    ExperienceStore,
)


class ExperienceMemory:
    """
    Central entry point for Experience OS.

    Coordinates:

    - learning
    - consolidation
    - recall
    - applicability
    - ranking
    """

    def __init__(
        self,
        store: ExperienceStore | None = None,
    ) -> None:
        self._store = store or ExperienceStore()

        self._builder = ExperienceBuilder()

        self._consolidator = ExperienceConsolidator(
            self._store,
        )

        self._recall = ExperienceRecall(
            self._store,
        )

        self._applicability = ExperienceApplicability()

        self._ranker = ExperienceRanker()

    @property
    def store(self) -> ExperienceStore:
        """Return the backing experience store."""
        return self._store

    # --------------------------------------------------
    # CRUD Operations
    # --------------------------------------------------

    def add(
        self,
        experience: Experience,
    ) -> Experience:
        """
        Add an experience.

        Duplicate experiences are consolidated automatically.
        """
        return self._consolidator.consolidate(
            experience,
        )

    def store_experience(
        self,
        experience: Experience,
    ) -> Experience:
        """
        Backward-compatible alias for add().
        """
        return self.add(experience)

    def get(
        self,
        experience_id: UUID,
    ) -> Experience | None:
        """
        Retrieve an experience by ID.
        """
        for experience in self._store.all():
            if experience.id == experience_id:
                return experience

        return None

    def exists(
        self,
        experience_id: UUID,
    ) -> bool:
        """
        Return True if the experience exists.
        """
        return self.get(experience_id) is not None

    def remove(
        self,
        experience_id: UUID,
    ) -> bool:
        """
        Remove an experience.
        """
        if not self.exists(experience_id):
            return False

        self._store.remove(experience_id)
        return True

    def all(
        self,
    ) -> list[Experience]:
        """
        Return all experiences.
        """
        return self._store.all()

    def count(
        self,
    ) -> int:
        """
        Number of stored experiences.
        """
        return len(self._store.all())

    def clear(
        self,
    ) -> None:
        """
        Remove every stored experience.
        """
        self._store.clear()

    # --------------------------------------------------
    # Learning
    # --------------------------------------------------

    def learn(
        self,
        task: Task,
        decision: Decision,
        outcome: Outcome,
    ) -> Experience | None:
        """
        Learn a new experience from execution.
        """

        experience = self._builder.build(
            task,
            decision,
            outcome,
        )

        if experience is None:
            return None

        return self.add(experience)

    # --------------------------------------------------
    # Recall
    # --------------------------------------------------

    def retrieve(
        self,
        task: Task,
    ) -> list[Experience]:
        """
        Retrieve ranked applicable experiences.
        """

        recalled = self._recall.recall(task)

        applicable: list[Experience] = []

        for experience in recalled:
            result = self._applicability.evaluate(
                experience,
                task,
            )

            if result.status.name == "APPLY":
                applicable.append(experience)

        ranked = self._ranker.rank(
            applicable,
            task,
        )

        return [
            score.experience
            for score in ranked
        ]

    def best(
        self,
        task: Task,
    ) -> Experience | None:
        """
        Return the highest-ranked experience.
        """

        experiences = self.retrieve(task)

        if not experiences:
            return None

        return experiences[0]