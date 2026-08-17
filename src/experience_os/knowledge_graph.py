from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    Task,
)


class NodeType(StrEnum):
    TASK = "task"
    DECISION = "decision"
    OUTCOME = "outcome"
    EXPERIENCE = "experience"


class RelationType(StrEnum):
    GENERATED = "generated"
    PRODUCED = "produced"
    USED = "used"
    RELATED = "related"


@dataclass(slots=True, frozen=True)
class KnowledgeNode:
    id: UUID
    type: NodeType
    value: object


@dataclass(slots=True, frozen=True)
class KnowledgeEdge:
    source: UUID
    target: UUID
    relation: RelationType


class KnowledgeGraph:
    """
    Lightweight in-memory knowledge graph.

    Nodes represent Tasks, Decisions, Outcomes and Experiences.

    Edges represent semantic relationships between them.

    Future versions may migrate to Neo4j or Memgraph.
    """

    def __init__(self) -> None:
        self._nodes: dict[UUID, KnowledgeNode] = {}

        self._edges: dict[
            UUID,
            list[KnowledgeEdge],
        ] = defaultdict(list)

    # -----------------------------------------------------
    # Node creation
    # -----------------------------------------------------

    def add_task(
        self,
        task: Task,
    ) -> UUID:

        self._nodes[task.id] = KnowledgeNode(
            id=task.id,
            type=NodeType.TASK,
            value=task,
        )

        return task.id

    def add_decision(
        self,
        decision: Decision,
    ) -> UUID:

        self._nodes[decision.id] = KnowledgeNode(
            id=decision.id,
            type=NodeType.DECISION,
            value=decision,
        )

        return decision.id

    def add_outcome(
        self,
        outcome: Outcome,
    ) -> UUID:

        node_id = UUID(int=hash(outcome.description) & ((1 << 128) - 1))

        self._nodes[node_id] = KnowledgeNode(
            id=node_id,
            type=NodeType.OUTCOME,
            value=outcome,
        )

        return node_id

    def add_experience(
        self,
        experience: Experience,
    ) -> UUID:

        self._nodes[experience.id] = KnowledgeNode(
            id=experience.id,
            type=NodeType.EXPERIENCE,
            value=experience,
        )

        return experience.id

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    def connect(
        self,
        source: UUID,
        target: UUID,
        relation: RelationType,
    ) -> None:

        self._edges[source].append(
            KnowledgeEdge(
                source=source,
                target=target,
                relation=relation,
            )
        )

    # -----------------------------------------------------
    # Queries
    # -----------------------------------------------------

    def node(
        self,
        node_id: UUID,
    ) -> KnowledgeNode | None:

        return self._nodes.get(node_id)

    def successors(
        self,
        node_id: UUID,
    ) -> list[KnowledgeNode]:

        result: list[KnowledgeNode] = []

        for edge in self._edges.get(node_id, []):

            node = self._nodes.get(edge.target)

            if node is not None:
                result.append(node)

        return result

    def predecessors(
        self,
        node_id: UUID,
    ) -> list[KnowledgeNode]:

        result: list[KnowledgeNode] = []

        for source, edges in self._edges.items():

            for edge in edges:

                if edge.target == node_id:

                    node = self._nodes.get(source)

                    if node is not None:
                        result.append(node)

        return result

    def edges(
        self,
        node_id: UUID,
    ) -> list[KnowledgeEdge]:

        return list(
            self._edges.get(node_id, [])
        )

    def node_count(
        self,
    ) -> int:

        return len(self._nodes)

    def edge_count(
        self,
    ) -> int:

        return sum(
            len(edges)
            for edges in self._edges.values()
        )

    def clear(
        self,
    ) -> None:

        self._nodes.clear()
        self._edges.clear()