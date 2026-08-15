from experience_os.models import Experience, Task
from experience_os.planner import (
    DeterministicPlanner,
    ExperienceInformedPlanner,
)
from experience_os.recall import ExperienceRecall, ExperienceStore


def test_family_task_uses_total_cost_decision() -> None:
    planner = DeterministicPlanner()

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
        constraints={"max_budget": 80000},
    )

    result = planner.plan(task)

    assert result.decision.description == "Compare total trip cost"
    assert "ticket_price_only" in result.decision.alternatives
    assert "compare_total_trip_cost" in result.decision.alternatives
    assert result.used_experience is None


def test_non_family_task_uses_constraint_based_decision() -> None:
    planner = DeterministicPlanner()

    task = Task(
        goal="Book a business flight",
        context={"traveler_type": "business"},
        constraints={"max_budget": 50000},
    )

    result = planner.plan(task)

    assert (
        result.decision.description
        == "Compare available options against task constraints"
    )
    assert result.used_experience is None


def test_planner_is_reproducible() -> None:
    planner = DeterministicPlanner()

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
        constraints={"max_budget": 80000},
    )

    first = planner.plan(task)
    second = planner.plan(task)

    assert first.decision.description == second.decision.description
    assert first.decision.rationale == second.decision.rationale
    assert first.decision.alternatives == second.decision.alternatives


def test_experience_informed_planner_reuses_applicable_experience() -> None:
    store = ExperienceStore()

    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["Check baggage before comparing price"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    store.add(experience)

    recall = ExperienceRecall(store)
    planner = ExperienceInformedPlanner(recall)

    task = Task(
        goal="Book an international family flight",
        context={
            "traveler_type": "family",
            "checked_baggage": True,
        },
    )

    result = planner.plan(task)

    assert result.decision.description == (
        "Check baggage before comparing price"
    )
    assert result.used_experience is not None
    assert result.used_experience.id == experience.id


def test_experience_informed_planner_rejects_conflicting_experience() -> None:
    store = ExperienceStore()

    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["Check baggage before comparing price"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    store.add(experience)

    recall = ExperienceRecall(store)
    planner = ExperienceInformedPlanner(recall)

    task = Task(
        goal="Book a business flight",
        context={
            "traveler_type": "business",
            "checked_baggage": True,
        },
    )

    result = planner.plan(task)

    assert (
        result.decision.description
        == "Compare available options against task constraints"
    )
    assert result.used_experience is None


def test_experience_informed_planner_rejects_uncertain_experience() -> None:
    store = ExperienceStore()

    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["Check baggage before comparing price"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    store.add(experience)

    recall = ExperienceRecall(store)
    planner = ExperienceInformedPlanner(recall)

    task = Task(
        goal="Book a family flight",
        context={
            "traveler_type": "family",
        },
    )

    result = planner.plan(task)

    # The experience is not reused because the baggage condition
    # is missing. The normal family baseline is used.
    assert result.decision.description == "Compare total trip cost"
    assert result.used_experience is None


def test_experience_informed_planner_falls_back_without_experience() -> None:
    store = ExperienceStore()

    recall = ExperienceRecall(store)
    planner = ExperienceInformedPlanner(recall)

    task = Task(
        goal="Book a business flight",
        context={"traveler_type": "business"},
        constraints={"max_budget": 50000},
    )

    result = planner.plan(task)

    assert (
        result.decision.description
        == "Compare available options against task constraints"
    )
    assert result.used_experience is None


def test_highest_ranked_experience_is_selected() -> None:
    store = ExperienceStore()

    weak_experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Use weak strategy"],
        execution_count=5,
        successful_executions=4,
        confidence=0.8,
    )

    strong_experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Use strong strategy"],
        execution_count=10,
        successful_executions=10,
        confidence=1.0,
    )

    store.add(weak_experience)
    store.add(strong_experience)

    recall = ExperienceRecall(store)
    planner = ExperienceInformedPlanner(recall)

    task = Task(
        goal="Book a family flight",
        context={"traveler_type": "family"},
    )

    result = planner.plan(task)

    assert result.used_experience is not None
    assert result.used_experience.id == strong_experience.id
    assert result.decision.description == "Use strong strategy"