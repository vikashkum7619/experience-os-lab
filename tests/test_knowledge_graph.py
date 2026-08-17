from __future__ import annotations

from experience_os.knowledge_graph import (
    KnowledgeGraph,
    NodeType,
    RelationType,
)
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)


def build_task() -> Task:
    return Task(
        goal="Book flight",
    )


def build_decision() -> Decision:
    return Decision(
        description="Compare airlines",
        rationale="Lowest total cost",
    )


def build_outcome() -> Outcome:
    return Outcome(
        status=OutcomeStatus.SUCCESS,
        score=0.95,
        description="Booking completed",
    )


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


def test_add_task() -> None:
    graph = KnowledgeGraph()

    task = build_task()

    node_id = graph.add_task(task)

    node = graph.node(node_id)

    assert node is not None
    assert node.type is NodeType.TASK
    assert node.value == task


def test_add_decision() -> None:
    graph = KnowledgeGraph()

    decision = build_decision()

    node_id = graph.add_decision(decision)

    node = graph.node(node_id)

    assert node is not None
    assert node.type is NodeType.DECISION
    assert node.value == decision


def test_add_outcome() -> None:
    graph = KnowledgeGraph()

    outcome = build_outcome()

    node_id = graph.add_outcome(outcome)

    node = graph.node(node_id)

    assert node is not None
    assert node.type is NodeType.OUTCOME
    assert node.value == outcome


def test_add_experience() -> None:
    graph = KnowledgeGraph()

    experience = build_experience()

    node_id = graph.add_experience(experience)

    node = graph.node(node_id)

    assert node is not None
    assert node.type is NodeType.EXPERIENCE
    assert node.value == experience


def test_connect_nodes() -> None:
    graph = KnowledgeGraph()

    task = build_task()
    decision = build_decision()

    task_id = graph.add_task(task)
    decision_id = graph.add_decision(decision)

    graph.connect(
        task_id,
        decision_id,
        RelationType.GENERATED,
    )

    assert graph.edge_count() == 1


def test_successors() -> None:
    graph = KnowledgeGraph()

    task = build_task()
    decision = build_decision()

    task_id = graph.add_task(task)
    decision_id = graph.add_decision(decision)

    graph.connect(
        task_id,
        decision_id,
        RelationType.GENERATED,
    )

    successors = graph.successors(task_id)

    assert len(successors) == 1
    assert successors[0].value == decision


def test_predecessors() -> None:
    graph = KnowledgeGraph()

    task = build_task()
    decision = build_decision()

    task_id = graph.add_task(task)
    decision_id = graph.add_decision(decision)

    graph.connect(
        task_id,
        decision_id,
        RelationType.GENERATED,
    )

    predecessors = graph.predecessors(decision_id)

    assert len(predecessors) == 1
    assert predecessors[0].value == task


def test_edges() -> None:
    graph = KnowledgeGraph()

    task = build_task()
    decision = build_decision()

    task_id = graph.add_task(task)
    decision_id = graph.add_decision(decision)

    graph.connect(
        task_id,
        decision_id,
        RelationType.GENERATED,
    )

    edges = graph.edges(task_id)

    assert len(edges) == 1
    assert edges[0].relation is RelationType.GENERATED


def test_node_count() -> None:
    graph = KnowledgeGraph()

    graph.add_task(build_task())
    graph.add_decision(build_decision())
    graph.add_experience(build_experience())

    assert graph.node_count() == 3


def test_edge_count() -> None:
    graph = KnowledgeGraph()

    task = build_task()
    decision = build_decision()
    experience = build_experience()

    task_id = graph.add_task(task)
    decision_id = graph.add_decision(decision)
    experience_id = graph.add_experience(experience)

    graph.connect(
        task_id,
        decision_id,
        RelationType.GENERATED,
    )

    graph.connect(
        decision_id,
        experience_id,
        RelationType.PRODUCED,
    )

    assert graph.edge_count() == 2


def test_node_returns_none() -> None:
    graph = KnowledgeGraph()

    task = build_task()

    graph.add_task(task)

    assert graph.node(build_experience().id) is None


def test_clear() -> None:
    graph = KnowledgeGraph()

    task = build_task()
    decision = build_decision()

    task_id = graph.add_task(task)
    decision_id = graph.add_decision(decision)

    graph.connect(
        task_id,
        decision_id,
        RelationType.GENERATED,
    )

    graph.clear()

    assert graph.node_count() == 0
    assert graph.edge_count() == 0


def test_multiple_relationships() -> None:
    graph = KnowledgeGraph()

    task = build_task()
    decision = build_decision()
    outcome = build_outcome()
    experience = build_experience()

    task_id = graph.add_task(task)
    decision_id = graph.add_decision(decision)
    outcome_id = graph.add_outcome(outcome)
    experience_id = graph.add_experience(experience)

    graph.connect(
        task_id,
        decision_id,
        RelationType.GENERATED,
    )

    graph.connect(
        decision_id,
        outcome_id,
        RelationType.PRODUCED,
    )

    graph.connect(
        outcome_id,
        experience_id,
        RelationType.GENERATED,
    )

    assert graph.node_count() == 4
    assert graph.edge_count() == 3

    assert len(graph.successors(task_id)) == 1
    assert len(graph.successors(decision_id)) == 1
    assert len(graph.successors(outcome_id)) == 1