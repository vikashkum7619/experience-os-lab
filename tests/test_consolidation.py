from __future__ import annotations

from experience_os.consolidation import ExperienceConsolidator
from experience_os.models import Experience
from experience_os.recall import ExperienceStore


def test_new_experience_is_added_to_store() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=1,
        successful_executions=1,
        confidence=1.0,
    )

    result = consolidator.consolidate(experience)

    assert result.id == experience.id
    assert len(store.all()) == 1


def test_duplicate_experience_is_merged() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    first = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    second = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=3,
        successful_executions=2,
        confidence=0.66,
    )

    consolidator.consolidate(first)
    consolidator.consolidate(second)

    assert len(store.all()) == 1

    merged = store.all()[0]

    assert merged.execution_count == 8
    assert merged.successful_executions == 7


def test_different_conditions_create_new_experience() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    first = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
    )

    second = Experience(
        conditions={"traveler_type": "business"},
        decision_pattern=["Compare total trip cost"],
    )

    consolidator.consolidate(first)
    consolidator.consolidate(second)

    assert len(store.all()) == 2


def test_different_decision_pattern_creates_new_experience() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    first = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
    )

    second = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Check baggage before comparing price"],
    )

    consolidator.consolidate(first)
    consolidator.consolidate(second)

    assert len(store.all()) == 2


def test_confidence_is_recalculated_after_merge() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    first = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=4,
        successful_executions=4,
        confidence=1.0,
    )

    second = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=6,
        successful_executions=3,
        confidence=0.5,
    )

    consolidator.consolidate(first)
    consolidator.consolidate(second)

    merged = store.all()[0]

    assert merged.execution_count == 10
    assert merged.successful_executions == 7
    assert merged.confidence == 0.7


def test_higher_confidence_decision_pattern_replaces_existing() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    original = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Old strategy"],
        execution_count=5,
        successful_executions=4,
        confidence=0.8,
    )

    improved = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Improved strategy"],
        execution_count=2,
        successful_executions=2,
        confidence=1.0,
    )

    consolidator.consolidate(original)
    consolidator.merge(original, improved)

    assert original.decision_pattern == ["Improved strategy"]


def test_lower_confidence_does_not_replace_decision_pattern() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    original = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Best strategy"],
        execution_count=10,
        successful_executions=10,
        confidence=1.0,
    )

    weaker = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Weak strategy"],
        execution_count=2,
        successful_executions=1,
        confidence=0.5,
    )

    consolidator.consolidate(original)
    consolidator.merge(original, weaker)

    assert original.decision_pattern == ["Best strategy"]


def test_find_duplicate_returns_existing_experience() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
    )

    consolidator.consolidate(experience)

    duplicate = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
    )

    found = consolidator.find_duplicate(duplicate)

    assert found is not None
    assert found.id == experience.id


def test_find_duplicate_returns_none_when_not_found() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
    )

    found = consolidator.find_duplicate(experience)

    assert found is None


def test_consolidate_returns_existing_after_merge() -> None:
    store = ExperienceStore()
    consolidator = ExperienceConsolidator(store)

    first = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
    )

    second = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
    )

    consolidator.consolidate(first)
    result = consolidator.consolidate(second)

    assert result.id == first.id