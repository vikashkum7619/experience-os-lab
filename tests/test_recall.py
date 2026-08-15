from experience_os.models import (
    ApplicabilityStatus,
    Experience,
    Task,
)
from experience_os.recall import (
    ExperienceApplicability,
    ExperienceRecall,
    ExperienceStore,
)


def test_matching_experience_is_recalled() -> None:
    store = ExperienceStore()

    experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    store.add(experience)

    recall = ExperienceRecall(store)

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
    )

    matches = recall.recall(task)

    assert len(matches) == 1
    assert matches[0].id == experience.id


def test_non_matching_experience_is_not_recalled() -> None:
    store = ExperienceStore()

    experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    store.add(experience)

    recall = ExperienceRecall(store)

    task = Task(
        goal="Book a business flight",
        context={"traveler_type": "business"},
    )

    matches = recall.recall(task)

    assert matches == []


def test_partial_match_is_recalled_as_candidate() -> None:
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

    task = Task(
        goal="Book a family flight",
        context={
            "traveler_type": "family",
        },
    )

    matches = recall.recall(task)

    assert len(matches) == 1
    assert matches[0].id == experience.id


def test_multiple_candidates_are_recalled() -> None:
    store = ExperienceStore()

    family_experience = Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Compare total trip cost"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    baggage_experience = Experience(
        conditions={"checked_baggage": True},
        decision_pattern=["Check baggage before comparing price"],
        execution_count=3,
        successful_executions=3,
        confidence=1.0,
    )

    unrelated_experience = Experience(
        conditions={"traveler_type": "business"},
        decision_pattern=["Use business travel strategy"],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    store.add(family_experience)
    store.add(baggage_experience)
    store.add(unrelated_experience)

    recall = ExperienceRecall(store)

    task = Task(
        goal="Book a family flight with baggage",
        context={
            "traveler_type": "family",
            "checked_baggage": True,
        },
    )

    matches = recall.recall(task)

    assert len(matches) == 2
    assert family_experience in matches
    assert baggage_experience in matches
    assert unrelated_experience not in matches


def test_empty_store_returns_no_experiences() -> None:
    store = ExperienceStore()
    recall = ExperienceRecall(store)

    task = Task(
        goal="Book a flight",
        context={"traveler_type": "family"},
    )

    matches = recall.recall(task)

    assert matches == []


def test_applicability_applies_when_all_conditions_match() -> None:
    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["Check baggage before comparing price"],
        execution_count=10,
        successful_executions=9,
        confidence=0.9,
    )

    task = Task(
        goal="Book a family flight",
        context={
            "traveler_type": "family",
            "checked_baggage": True,
        },
    )

    evaluator = ExperienceApplicability()

    result = evaluator.evaluate(experience, task)

    assert result.status == ApplicabilityStatus.APPLY
    assert result.matched_conditions == [
        "traveler_type",
        "checked_baggage",
    ]
    assert result.mismatched_conditions == []
    assert result.uncertain_conditions == []


def test_applicability_rejects_conflicting_condition() -> None:
    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["Check baggage before comparing price"],
        execution_count=10,
        successful_executions=9,
        confidence=0.9,
    )

    task = Task(
        goal="Book a business flight",
        context={
            "traveler_type": "business",
            "checked_baggage": True,
        },
    )

    evaluator = ExperienceApplicability()

    result = evaluator.evaluate(experience, task)

    assert result.status == ApplicabilityStatus.REJECT
    assert "traveler_type" in result.mismatched_conditions


def test_applicability_is_uncertain_when_condition_is_missing() -> None:
    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["Check baggage before comparing price"],
        execution_count=10,
        successful_executions=9,
        confidence=0.9,
    )

    task = Task(
        goal="Book a family flight",
        context={
            "traveler_type": "family",
        },
    )

    evaluator = ExperienceApplicability()

    result = evaluator.evaluate(experience, task)

    assert result.status == ApplicabilityStatus.UNCERTAIN
    assert result.matched_conditions == ["traveler_type"]
    assert result.uncertain_conditions == ["checked_baggage"]


def test_applicability_handles_multiple_conflicts() -> None:
    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["Check baggage before comparing price"],
        execution_count=10,
        successful_executions=9,
        confidence=0.9,
    )

    task = Task(
        goal="Book a business flight",
        context={
            "traveler_type": "business",
            "checked_baggage": False,
        },
    )

    evaluator = ExperienceApplicability()

    result = evaluator.evaluate(experience, task)

    assert result.status == ApplicabilityStatus.REJECT
    assert set(result.mismatched_conditions) == {
        "traveler_type",
        "checked_baggage",
    }