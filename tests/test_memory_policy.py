from __future__ import annotations

from experience_os.memory_policy import (
    MemoryAction,
    MemoryPolicy,
)
from experience_os.models import Experience


def build_experience(
    *,
    confidence: float = 0.90,
    execution_count: int = 10,
    successful_executions: int = 9,
) -> Experience:
    return Experience(
        conditions={
            "traveler": "family",
        },
        decision_pattern=[
            "compare airlines",
            "book direct",
        ],
        execution_count=execution_count,
        successful_executions=successful_executions,
        confidence=confidence,
    )


def test_ignore_low_confidence() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        confidence=0.40,
        execution_count=10,
    )

    decision = policy.evaluate(experience)

    assert decision.action is MemoryAction.IGNORE
    assert "confidence" in decision.reason.lower()


def test_update_insufficient_executions() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        confidence=0.90,
        execution_count=2,
    )

    decision = policy.evaluate(experience)

    assert decision.action is MemoryAction.UPDATE
    assert "evidence" in decision.reason.lower()


def test_save_valid_memory() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        confidence=0.90,
        execution_count=10,
    )

    decision = policy.evaluate(experience)

    assert decision.action is MemoryAction.SAVE


def test_archive_high_quality_memory() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        confidence=0.97,
        execution_count=120,
        successful_executions=118,
    )

    decision = policy.evaluate(experience)

    assert decision.action is MemoryAction.ARCHIVE
    assert "stable" in decision.reason.lower()


def test_should_save_true_for_save() -> None:
    policy = MemoryPolicy()

    experience = build_experience()

    assert policy.should_save(experience)


def test_should_save_true_for_update() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        execution_count=1,
    )

    assert policy.should_save(experience)


def test_should_save_true_for_archive() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        confidence=0.98,
        execution_count=150,
        successful_executions=149,
    )

    assert policy.should_save(experience)


def test_should_save_false_for_ignore() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        confidence=0.20,
    )

    assert not policy.should_save(experience)


def test_archive_candidate_true() -> None:
    policy = MemoryPolicy()

    experience = build_experience(
        confidence=0.99,
        execution_count=100,
        successful_executions=99,
    )

    assert policy.is_archive_candidate(experience)


def test_archive_candidate_false() -> None:
    policy = MemoryPolicy()

    experience = build_experience()

    assert not policy.is_archive_candidate(experience)


def test_custom_confidence_threshold() -> None:
    policy = MemoryPolicy(
        minimum_confidence=0.80,
    )

    experience = build_experience(
        confidence=0.75,
    )

    decision = policy.evaluate(experience)

    assert decision.action is MemoryAction.IGNORE


def test_custom_execution_threshold() -> None:
    policy = MemoryPolicy(
        minimum_executions=5,
    )

    experience = build_experience(
        execution_count=4,
    )

    decision = policy.evaluate(experience)

    assert decision.action is MemoryAction.UPDATE


def test_minimum_confidence_property() -> None:
    policy = MemoryPolicy(
        minimum_confidence=0.75,
    )

    assert policy.minimum_confidence == 0.75


def test_minimum_execution_property() -> None:
    policy = MemoryPolicy(
        minimum_executions=8,
    )

    assert policy.minimum_executions == 8