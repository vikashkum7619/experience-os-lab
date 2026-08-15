from __future__ import annotations

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
from experience_os.recall_strategy import ExactRecallStrategy


def make_task() -> Task:
    return Task(
        goal="Book a flight",
        context={
            "traveler_type": "family",
            "checked_baggage": True,
        },
    )


def test_exact_recall_returns_candidate_with_partial_overlap() -> None:
    store = ExperienceStore()

    experience = Experience(
        conditions={
            "traveler_type": "business",
            "checked_baggage": True,
        },
        decision_pattern=[
            "Business strategy",
        ],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    store.add(experience)

    recall = ExperienceRecall(store)
    strategy = ExactRecallStrategy(recall)

    results = strategy.recall(make_task())

    # Candidate recall only requires one matching condition.
    assert len(results) == 1
    assert results[0].id == experience.id


def test_candidate_is_rejected_by_applicability() -> None:
    experience = Experience(
        conditions={
            "traveler_type": "business",
            "checked_baggage": True,
        },
        decision_pattern=[
            "Business strategy",
        ],
        execution_count=5,
        successful_executions=5,
        confidence=1.0,
    )

    result = ExperienceApplicability().evaluate(
        experience,
        make_task(),
    )

    assert result.status == ApplicabilityStatus.REJECT