from __future__ import annotations

from experience_os.lifecycle import (
    ExperienceLifecycle,
    ExperienceState,
    LifecyclePolicy,
)
from experience_os.models import Experience


def make_experience(
    *,
    confidence: float,
    executions: int,
    successes: int | None = None,
) -> Experience:
    if successes is None:
        successes = executions

    return Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=[
            "Check baggage before comparing price",
        ],
        execution_count=executions,
        successful_executions=successes,
        confidence=confidence,
    )


def test_new_experience_is_candidate() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=1.0,
        executions=0,
    )

    assert (
        lifecycle.state(experience)
        == ExperienceState.CANDIDATE
    )


def test_low_execution_experience_is_candidate() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=1.0,
        executions=3,
    )

    assert (
        lifecycle.state(experience)
        == ExperienceState.CANDIDATE
    )


def test_validated_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.70,
        executions=10,
    )

    assert (
        lifecycle.state(experience)
        == ExperienceState.VALIDATED
    )


def test_trusted_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.85,
        executions=10,
    )

    assert (
        lifecycle.state(experience)
        == ExperienceState.TRUSTED
    )


def test_expert_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.98,
        executions=25,
    )

    assert (
        lifecycle.state(experience)
        == ExperienceState.EXPERT
    )


def test_retired_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.20,
        executions=20,
    )

    assert (
        lifecycle.state(experience)
        == ExperienceState.RETIRED
    )


def test_active_experience() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.90,
        executions=10,
    )

    assert lifecycle.is_active(experience)


def test_retired_experience_not_active() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.20,
        executions=10,
    )

    assert not lifecycle.is_active(experience)


def test_should_promote_candidate() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.50,
        executions=10,
    )

    assert not lifecycle.should_promote(
        experience,
    )


def test_should_promote_validated() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.70,
        executions=10,
    )

    assert lifecycle.should_promote(
        experience,
    )


def test_should_retire() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.10,
        executions=10,
    )

    assert lifecycle.should_retire(
        experience,
    )


def test_should_not_retire() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.95,
        executions=10,
    )

    assert not lifecycle.should_retire(
        experience,
    )


def test_archive_returns_archived_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=1.0,
        executions=20,
    )

    assert (
        lifecycle.archive(experience)
        == ExperienceState.ARCHIVED
    )


def test_promote_returns_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.82,
        executions=10,
    )

    assert (
        lifecycle.promote(experience)
        == ExperienceState.TRUSTED
    )


def test_demote_recalculates_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.45,
        executions=10,
    )

    assert (
        lifecycle.demote(experience)
        == ExperienceState.CANDIDATE
    )


def test_refresh_returns_current_state() -> None:
    lifecycle = ExperienceLifecycle()

    experience = make_experience(
        confidence=0.98,
        executions=20,
    )

    assert (
        lifecycle.refresh(experience)
        == ExperienceState.EXPERT
    )


def test_custom_policy_changes_thresholds() -> None:
    lifecycle = ExperienceLifecycle(
        LifecyclePolicy(
            validated_threshold=0.50,
            trusted_threshold=0.60,
            expert_threshold=0.70,
            retire_threshold=0.20,
            minimum_executions=2,
        )
    )

    experience = make_experience(
        confidence=0.75,
        executions=3,
    )

    assert (
        lifecycle.state(experience)
        == ExperienceState.EXPERT
    )