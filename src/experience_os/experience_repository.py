from __future__ import annotations

from pathlib import Path
from uuid import UUID

from experience_os.experience_graph import ExperienceGraph
from experience_os.lifecycle import (
    ExperienceLifecycle,
    ExperienceState,
)
from experience_os.memory import ExperienceMemory
from experience_os.models import Experience
from experience_os.storage import ExperienceStorage


class ExperienceRepository:
    """
    Central access point for Experience OS.

    Responsibilities
    ----------------
    - Persist experiences
    - Maintain in-memory cache
    - Maintain graph
    - Evaluate lifecycle
    """

    def __init__(
        self,
        storage: ExperienceStorage,
        memory: ExperienceMemory | None = None,
        graph: ExperienceGraph | None = None,
        lifecycle: ExperienceLifecycle | None = None,
    ) -> None:
        self._storage = storage
        self._memory = memory or ExperienceMemory()
        self._graph = graph or ExperienceGraph()
        self._lifecycle = lifecycle or ExperienceLifecycle()

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def storage(self) -> ExperienceStorage:
        return self._storage

    @property
    def memory(self) -> ExperienceMemory:
        return self._memory

    @property
    def graph(self) -> ExperienceGraph:
        return self._graph

    # --------------------------------------------------
    # CRUD
    # --------------------------------------------------

    def add(
        self,
        experience: Experience,
    ) -> None:
        """
        Add an experience.
        """
        self._memory.add(experience)
        self._graph.add_experience(experience)

    def update(
        self,
        experience: Experience,
    ) -> None:
        """
        Replace an existing experience.
        """
        self._memory.remove(experience.id)
        self._memory.add(experience)

    def remove(
        self,
        experience_id: UUID,
    ) -> bool:
        """
        Remove an experience.

        Returns True if removed.
        """
        if not self.exists(experience_id):
            return False

        self._memory.remove(experience_id)
        return True

    def exists(
        self,
        experience_id: UUID,
    ) -> bool:
        return self.get(experience_id) is not None

    def get(
        self,
        experience_id: UUID,
    ) -> Experience | None:
        return self._memory.get(experience_id)

    def all(
        self,
    ) -> list[Experience]:
        return self._memory.all()

    def count(
        self,
    ) -> int:
        return self._memory.count()

    # --------------------------------------------------
    # Persistence
    # --------------------------------------------------

    def save(self) -> None:
        """
        Persist all experiences.
        """
        self._storage.save(
            self._memory.all(),
        )

    def load(self) -> None:
        """
        Load experiences from storage.
        """
        self._memory.clear()
        self._graph.clear()

        for experience in self._storage.load():
            self._memory.add(experience)
            self._graph.add_experience(experience)

    def clear(self) -> None:
        """
        Remove every experience.
        """
        self._memory.clear()
        self._graph.clear()
        self._storage.clear()

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def state(
        self,
        experience: Experience,
    ) -> ExperienceState:
        return self._lifecycle.state(experience)

    def archive(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Archive an experience.
        """
        return self._lifecycle.archive(experience)

    def promote(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Promote an experience.
        """
        return self._lifecycle.promote(experience)

    def demote(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Demote an experience.
        """
        return self._lifecycle.demote(experience)

    def refresh(
        self,
        experience: Experience,
    ) -> ExperienceState:
        """
        Refresh lifecycle state.
        """
        return self._lifecycle.refresh(experience)

    def active(
        self,
    ) -> list[Experience]:
        """
        Return active experiences.
        """
        return [
            experience
            for experience in self._memory.all()
            if self._lifecycle.is_active(experience)
        ]

    # --------------------------------------------------
    # Graph
    # --------------------------------------------------

    def connect(
        self,
        source: Experience,
        target: Experience,
    ) -> None:
        self._graph.connect(
            source,
            target,
        )

    def successors(
        self,
        experience: Experience,
    ) -> list[Experience]:
        return self._graph.successors(
            experience,
        )

    def predecessors(
        self,
        experience: Experience,
    ) -> list[Experience]:
        return self._graph.predecessors(
            experience,
        )

    # --------------------------------------------------
    # Constructors
    # --------------------------------------------------

    @classmethod
    def from_path(
        cls,
        path: Path,
    ) -> "ExperienceRepository":
        """
        Create a repository backed by a storage file.
        """
        repository = cls(
            storage=ExperienceStorage(path),
        )

        repository.load()

        return repository