from __future__ import annotations

from experience_os.memory import ExperienceMemory
from experience_os.models import (
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
    Task,
)


def successful_outcome() -> Outcome:
    return Outcome(
        status=OutcomeStatus.SUCCESS,
        score=1.0,
        metrics={"accuracy": 1.0},
        description="Successful execution",
    )


def family_task() -> Task:
    return Task(
        goal="Book family flight",
        context={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        constraints={"max_budget": 80000},
    )


def business_task() -> Task:
    return Task(
        goal="Book business flight",
        context={
            "traveler_type": "business",
            "checked_baggage": True,
        },
    )


def baggage_decision() -> Decision:
    return Decision(
        description="Check baggage before comparing price",
        rationale="Reuse validated experience",
    )


def test_learn_stores_experience() -> None:
    memory = ExperienceMemory()

    experience = memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    assert experience is not None
    assert len(memory.all()) == 1


def test_store_experience_adds_experience() -> None:
    memory = ExperienceMemory()

    experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total cost"],
        execution_count=1,
        successful_executions=1,
        confidence=1.0,
    )

    stored = memory.store_experience(experience)

    assert stored.id == experience.id
    assert len(memory.all()) == 1


def test_best_returns_none_when_store_empty() -> None:
    memory = ExperienceMemory()

    assert memory.best(family_task()) is None


def test_retrieve_returns_matching_experience() -> None:
    memory = ExperienceMemory()

    memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    results = memory.retrieve(family_task())

    assert len(results) == 1
    assert (
        results[0].decision_pattern[0]
        == "Check baggage before comparing price"
    )


def test_retrieve_returns_empty_for_non_matching_task() -> None:
    memory = ExperienceMemory()

    memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    results = memory.retrieve(business_task())

    assert results == []


def test_best_returns_highest_ranked_experience() -> None:
    memory = ExperienceMemory()

    weak = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Weak strategy"],
        execution_count=2,
        successful_executions=1,
        confidence=0.4,
    )

    strong = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Strong strategy"],
        execution_count=10,
        successful_executions=10,
        confidence=1.0,
    )

    memory.store_experience(weak)
    memory.store_experience(strong)

    best = memory.best(
        Task(
            goal="Family flight",
            context={"traveler_type": "family"},
        )
    )

    assert best is not None
    assert best.decision_pattern[0] == "Strong strategy"


def test_all_returns_every_experience() -> None:
    memory = ExperienceMemory()

    memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    memory.learn(
        Task(
            goal="Business",
            context={
                "traveler_type": "business",
                "checked_baggage": True,
            },
        ),
        baggage_decision(),
        successful_outcome(),
    )

    assert len(memory.all()) == 2


def test_duplicate_learning_is_consolidated() -> None:
    memory = ExperienceMemory()

    memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    assert len(memory.all()) == 1

    experience = memory.all()[0]

    assert experience.execution_count >= 2


def test_retrieve_returns_ranked_order() -> None:
    memory = ExperienceMemory()

    low = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Low"],
        execution_count=2,
        successful_executions=1,
        confidence=0.5,
    )

    high = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["High"],
        execution_count=20,
        successful_executions=20,
        confidence=1.0,
    )

    memory.store_experience(low)
    memory.store_experience(high)

    results = memory.retrieve(
        Task(
            goal="Family",
            context={"traveler_type": "family"},
        )
    )

    assert results[0].decision_pattern[0] == "High"


def test_best_returns_same_as_first_retrieved() -> None:
    memory = ExperienceMemory()

    memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    retrieved = memory.retrieve(family_task())
    best = memory.best(family_task())

    assert best is not None
    assert best.id == retrieved[0].id


def test_learning_returns_created_experience() -> None:
    memory = ExperienceMemory()

    experience = memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    assert experience is not None
    assert experience.conditions["traveler_type"] == "family"


def test_end_to_end_learning_and_retrieval() -> None:
    memory = ExperienceMemory()

    learned = memory.learn(
        family_task(),
        baggage_decision(),
        successful_outcome(),
    )

    assert learned is not None

    retrieved = memory.best(family_task())

    assert retrieved is not None
    assert retrieved.id == learned.id