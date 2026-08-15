from __future__ import annotations

from experience_os.experience_metrics import (
    ExperienceMetrics,
    ExperienceMetricsCalculator,
)
from experience_os.models import (
    Experience,
    Outcome,
    OutcomeStatus,
)


def make_experience(
    execution_count: int = 10,
    successful_executions: int = 8,
    confidence: float = 0.8,
) -> Experience:
    return Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=[
            "Compare total cost",
        ],
        execution_count=execution_count,
        successful_executions=successful_executions,
        confidence=confidence,
    )


def make_outcome(
    status: OutcomeStatus = OutcomeStatus.SUCCESS,
    score: float = 1.0,
) -> Outcome:
    return Outcome(
        status=status,
        score=score,
        metrics={},
        description="Execution completed.",
    )


def test_calculator_returns_metrics() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(),
    )

    assert isinstance(
        metrics,
        ExperienceMetrics,
    )


def test_success_rate_calculated() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(
            execution_count=10,
            successful_executions=8,
        ),
    )

    assert metrics.success_rate == 0.8


def test_failure_rate_calculated() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(
            execution_count=10,
            successful_executions=8,
        ),
    )

    assert metrics.failure_rate == 0.2


def test_confidence_preserved() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(confidence=0.95),
    )

    assert metrics.confidence == 0.95


def test_execution_count_preserved() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(execution_count=7),
    )

    assert metrics.execution_count == 7


def test_successful_executions_preserved() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(successful_executions=6),
    )

    assert metrics.successful_executions == 6


def test_failed_executions_calculated() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(
            execution_count=10,
            successful_executions=6,
        ),
    )

    assert metrics.failed_executions == 4


def test_zero_execution_success_rate() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(
            execution_count=0,
            successful_executions=0,
        ),
    )

    assert metrics.success_rate == 0.0


def test_zero_execution_failure_rate() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(
            execution_count=0,
            successful_executions=0,
        ),
    )

    assert metrics.failure_rate == 0.0


def test_success_rate_method() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.success_rate(
        make_experience(),
    ) == 0.8


def test_failure_rate_method() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.failure_rate(
        make_experience(),
    ) == 0.2


def test_confidence_method() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.confidence(
        make_experience(confidence=0.9),
    ) == 0.9


def test_executions_method() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.executions(
        make_experience(execution_count=15),
    ) == 15


def test_successes_method() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.successes(
        make_experience(successful_executions=9),
    ) == 9


def test_failures_method() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.failures(
        make_experience(
            execution_count=10,
            successful_executions=7,
        ),
    ) == 3


def test_update_success_increments_execution() -> None:
    calculator = ExperienceMetricsCalculator()

    experience = make_experience()

    calculator.update(
        experience,
        make_outcome(),
    )

    assert experience.execution_count == 11


def test_update_success_increments_successes() -> None:
    calculator = ExperienceMetricsCalculator()

    experience = make_experience()

    calculator.update(
        experience,
        make_outcome(),
    )

    assert experience.successful_executions == 9


def test_update_failure_does_not_increment_successes() -> None:
    calculator = ExperienceMetricsCalculator()

    experience = make_experience()

    calculator.update(
        experience,
        make_outcome(
            status=OutcomeStatus.FAILURE,
            score=0.2,
        ),
    )

    assert experience.successful_executions == 8


def test_update_updates_confidence() -> None:
    calculator = ExperienceMetricsCalculator()

    experience = make_experience()

    calculator.update(
        experience,
        make_outcome(score=0.65),
    )

    assert experience.confidence == 0.65


def test_update_returns_metrics() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.update(
        make_experience(),
        make_outcome(),
    )

    assert isinstance(
        metrics,
        ExperienceMetrics,
    )


def test_is_reliable_true() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.is_reliable(
        make_experience(
            execution_count=10,
            successful_executions=9,
        ),
    )


def test_is_reliable_false_low_success_rate() -> None:
    calculator = ExperienceMetricsCalculator()

    assert not calculator.is_reliable(
        make_experience(
            execution_count=10,
            successful_executions=5,
        ),
    )


def test_is_reliable_false_low_execution_count() -> None:
    calculator = ExperienceMetricsCalculator()

    assert not calculator.is_reliable(
        make_experience(
            execution_count=2,
            successful_executions=2,
        ),
    )


def test_custom_reliability_threshold() -> None:
    calculator = ExperienceMetricsCalculator()

    assert calculator.is_reliable(
        make_experience(
            execution_count=3,
            successful_executions=2,
        ),
        minimum_success_rate=0.6,
        minimum_executions=3,
    )


def test_failure_count_never_negative() -> None:
    calculator = ExperienceMetricsCalculator()

    metrics = calculator.calculate(
        make_experience(
            execution_count=2,
            successful_executions=5,
        ),
    )

    assert metrics.failed_executions == 0