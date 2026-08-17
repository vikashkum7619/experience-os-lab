from __future__ import annotations

from datetime import UTC, datetime, timedelta

from experience_os.memory_optimizer import (
    MemoryOptimizer,
    OptimizationReport,
)
from experience_os.models import Experience


def build_experience(
    *,
    confidence: float = 0.90,
    execution_count: int = 10,
    successful_executions: int = 9,
    age_days: int = 0,
) -> Experience:
    now = datetime.now(UTC)

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
        created_at=now - timedelta(days=age_days),
        updated_at=now - timedelta(days=age_days),
    )


def test_remove_low_confidence() -> None:
    optimizer = MemoryOptimizer()

    experiences = [
        build_experience(confidence=0.95),
        build_experience(confidence=0.40),
    ]

    optimized = optimizer.remove_low_confidence(
        experiences,
    )

    assert len(optimized) == 1
    assert optimized[0].confidence == 0.95


def test_remove_stale() -> None:
    optimizer = MemoryOptimizer(
        maximum_age_days=30,
    )

    experiences = [
        build_experience(age_days=10),
        build_experience(age_days=60),
    ]

    optimized = optimizer.remove_stale(
        experiences,
    )

    assert len(optimized) == 1


def test_sort_by_importance() -> None:
    optimizer = MemoryOptimizer()

    low = build_experience(
        confidence=0.70,
        execution_count=5,
    )

    high = build_experience(
        confidence=0.95,
        execution_count=20,
    )

    ordered = optimizer.sort_by_importance(
        [
            low,
            high,
        ]
    )

    assert ordered[0] == high
    assert ordered[1] == low


def test_optimize_returns_report() -> None:
    optimizer = MemoryOptimizer()

    experiences = [
        build_experience(confidence=0.95),
        build_experience(confidence=0.30),
    ]

    optimized, report = optimizer.optimize(
        experiences,
    )

    assert len(optimized) == 1

    assert isinstance(
        report,
        OptimizationReport,
    )

    assert report.original_count == 2
    assert report.optimized_count == 1
    assert report.removed_count == 1


def test_empty_collection() -> None:
    optimizer = MemoryOptimizer()

    optimized, report = optimizer.optimize([])

    assert optimized == []

    assert report.original_count == 0
    assert report.optimized_count == 0
    assert report.removed_count == 0


def test_custom_confidence_threshold() -> None:
    optimizer = MemoryOptimizer(
        minimum_confidence=0.80,
    )

    experiences = [
        build_experience(confidence=0.75),
        build_experience(confidence=0.85),
    ]

    optimized = optimizer.remove_low_confidence(
        experiences,
    )

    assert len(optimized) == 1
    assert optimized[0].confidence == 0.85


def test_custom_age_threshold() -> None:
    optimizer = MemoryOptimizer(
        maximum_age_days=5,
    )

    experiences = [
        build_experience(age_days=3),
        build_experience(age_days=10),
    ]

    optimized = optimizer.remove_stale(
        experiences,
    )

    assert len(optimized) == 1


def test_minimum_confidence_property() -> None:
    optimizer = MemoryOptimizer(
        minimum_confidence=0.75,
    )

    assert optimizer.minimum_confidence == 0.75


def test_maximum_age_property() -> None:
    optimizer = MemoryOptimizer(
        maximum_age_days=180,
    )

    assert optimizer.maximum_age_days == 180


def test_already_optimized_collection() -> None:
    optimizer = MemoryOptimizer()

    experiences = [
        build_experience(
            confidence=0.95,
            execution_count=20,
        ),
        build_experience(
            confidence=0.90,
            execution_count=15,
        ),
    ]

    optimized, report = optimizer.optimize(
        experiences,
    )

    assert len(optimized) == 2

    assert report.original_count == 2
    assert report.optimized_count == 2
    assert report.removed_count == 0


def test_sort_keeps_highest_execution_when_confidence_equal() -> None:
    optimizer = MemoryOptimizer()

    first = build_experience(
        confidence=0.90,
        execution_count=5,
    )

    second = build_experience(
        confidence=0.90,
        execution_count=20,
    )

    ordered = optimizer.sort_by_importance(
        [
            first,
            second,
        ]
    )

    assert ordered[0].execution_count == 20


def test_sort_keeps_highest_success_rate_when_other_values_equal() -> None:
    optimizer = MemoryOptimizer()

    first = build_experience(
        confidence=0.90,
        execution_count=10,
        successful_executions=7,
    )

    second = build_experience(
        confidence=0.90,
        execution_count=10,
        successful_executions=9,
    )

    ordered = optimizer.sort_by_importance(
        [
            first,
            second,
        ]
    )

    assert ordered[0].successful_executions == 9


def test_remove_low_confidence_returns_empty() -> None:
    optimizer = MemoryOptimizer()

    experiences = [
        build_experience(confidence=0.20),
        build_experience(confidence=0.30),
    ]

    optimized = optimizer.remove_low_confidence(
        experiences,
    )

    assert optimized == []


def test_remove_stale_returns_empty() -> None:
    optimizer = MemoryOptimizer(
        maximum_age_days=1,
    )

    experiences = [
        build_experience(age_days=100),
        build_experience(age_days=200),
    ]

    optimized = optimizer.remove_stale(
        experiences,
    )

    assert optimized == []


def test_report_values_after_multiple_filters() -> None:
    optimizer = MemoryOptimizer(
        minimum_confidence=0.70,
        maximum_age_days=30,
    )

    experiences = [
        build_experience(confidence=0.90, age_days=5),
        build_experience(confidence=0.50, age_days=5),
        build_experience(confidence=0.90, age_days=100),
    ]

    optimized, report = optimizer.optimize(
        experiences,
    )

    assert len(optimized) == 1

    assert report.original_count == 3
    assert report.optimized_count == 1
    assert report.removed_count == 2