from __future__ import annotations

from datetime import UTC, datetime, timedelta

from experience_os.memory_lifecycle import MemoryLifecycle
from experience_os.models import Experience


def build_experience(
    *,
    confidence: float = 0.80,
    executions: int = 10,
    successes: int = 8,
    updated_at: datetime | None = None,
) -> Experience:

    return Experience(
        conditions={
            "task": "booking",
        },
        decision_pattern=[
            "compare prices",
        ],
        execution_count=executions,
        successful_executions=successes,
        confidence=confidence,
        updated_at=updated_at or datetime.now(UTC),
    )


def test_strengthen_increases_confidence() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.80,
        executions=10,
        successes=9,
    )

    lifecycle.strengthen(experience)

    assert experience.confidence > 0.80


def test_strengthen_does_not_exceed_one() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.99,
        executions=10,
        successes=10,
    )

    lifecycle.strengthen(experience)

    assert experience.confidence == 1.0


def test_strengthen_requires_good_success_rate() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.70,
        executions=10,
        successes=4,
    )

    lifecycle.strengthen(experience)

    assert experience.confidence == 0.70


def test_decay_reduces_confidence() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.80,
        updated_at=datetime.now(UTC) - timedelta(days=60),
    )

    lifecycle.decay(experience)

    assert experience.confidence < 0.80


def test_recent_memory_does_not_decay() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.80,
        updated_at=datetime.now(UTC) - timedelta(days=5),
    )

    lifecycle.decay(experience)

    assert experience.confidence == 0.80


def test_should_archive_returns_true() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.20,
    )

    assert lifecycle.should_archive(experience)


def test_should_archive_returns_false() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.80,
    )

    assert not lifecycle.should_archive(experience)


def test_should_forget_returns_true() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.05,
    )

    assert lifecycle.should_forget(experience)


def test_should_forget_returns_false() -> None:

    lifecycle = MemoryLifecycle()

    experience = build_experience(
        confidence=0.50,
    )

    assert not lifecycle.should_forget(experience)


def test_success_rate_property() -> None:

    experience = build_experience(
        executions=20,
        successes=15,
    )

    assert experience.success_rate == 0.75