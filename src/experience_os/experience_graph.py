from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from experience_os.models import Experience


@dataclass(frozen=True)
class ExperienceEdge:
    """
    Directed relationship between two experiences.
    """

    source: UUID
    target: UUID
    weight: int = 1


class ExperienceGraph:
    """
    Lightweight directed graph of experiences.

    Gen-1 keeps everything in memory.

    Future versions may replace this with Neo4j,
    Memgraph or another graph database.
    """

    def __init__(self) -> None:
        self._nodes: dict[UUID, Experience] = {}
        self._edges: dict[UUID, dict[UUID, int]] = defaultdict(dict)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    def add_experience(
        self,
        experience: Experience,
    ) -> None:
        self._nodes[experience.id] = experience

    def get(
        self,
        experience_id: UUID,
    ) -> Experience | None:
        return self._nodes.get(experience_id)

    def experiences(self) -> list[Experience]:
        return list(self._nodes.values())

    def count(self) -> int:
        return len(self._nodes)

    # --------------------------------------------------
    # Edges
    # --------------------------------------------------

    def connect(
        self,
        source: Experience,
        target: Experience,
    ) -> None:
        """
        Create or strengthen a transition.
        """

        self.add_experience(source)
        self.add_experience(target)

        current = self._edges[source.id].get(target.id, 0)
        self._edges[source.id][target.id] = current + 1

    def successors(
        self,
        experience: Experience,
    ) -> list[Experience]:
        """
        Immediate neighbours.
        """

        neighbours = self._edges.get(
            experience.id,
            {},
        )

        return [
            self._nodes[target]
            for target in neighbours
            if target in self._nodes
        ]

    def predecessors(
        self,
        experience: Experience,
    ) -> list[Experience]:
        """
        Reverse neighbours.
        """

        result: list[Experience] = []

        for source, targets in self._edges.items():
            if experience.id in targets:
                result.append(self._nodes[source])

        return result

    def edge_weight(
        self,
        source: Experience,
        target: Experience,
    ) -> int:
        """
        Transition frequency.
        """

        return self._edges.get(
            source.id,
            {},
        ).get(target.id, 0)

    def outgoing_count(
        self,
        experience: Experience,
    ) -> int:
        return len(
            self._edges.get(
                experience.id,
                {},
            )
        )

    def incoming_count(
        self,
        experience: Experience,
    ) -> int:
        total = 0

        for targets in self._edges.values():
            if experience.id in targets:
                total += 1

        return total

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()