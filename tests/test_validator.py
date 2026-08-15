from __future__ import annotations

from experience_os.models import (
    Outcome,
    OutcomeStatus,
)
from experience_os.validator import (
    ValidationResult,
    Validator,
)


def make_outcome(
    *,
    status: OutcomeStatus = OutcomeStatus.SUCCESS,
    score: float = 1.0,
    metrics: dict[str, float] | None = None,
    description: str = "Execution completed.",
) -> Outcome:
    return Outcome(
        status=status,
        score=score,
        metrics=metrics or {},
        description=description,
    )


# --------------------------------------------------
# Constructor
# --------------------------------------------------


def test_default_threshold() -> None:
    validator = Validator()

    assert validator.minimum_score == 0.70


def test_custom_threshold() -> None:
    validator = Validator(minimum_score=0.85)

    assert validator.minimum_score == 0.85


# --------------------------------------------------
# ValidationResult
# --------------------------------------------------


def test_validate_returns_validation_result() -> None:
    validator = Validator()

    result = validator.validate(make_outcome())

    assert isinstance(result, ValidationResult)


def test_validation_result_contains_original_outcome() -> None:
    validator = Validator()

    outcome = make_outcome()

    result = validator.validate(outcome)

    assert result.outcome == outcome


# --------------------------------------------------
# SUCCESS
# --------------------------------------------------


def test_success_is_valid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.SUCCESS,
        ),
    )

    assert result.is_valid


def test_success_reason_present() -> None:
    validator = Validator()

    result = validator.validate(make_outcome())

    assert result.reason != ""


def test_success_with_low_score_is_still_valid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.SUCCESS,
            score=0.05,
        ),
    )

    assert result.is_valid


# --------------------------------------------------
# FAILURE
# --------------------------------------------------


def test_failure_is_invalid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.FAILURE,
            score=1.0,
        ),
    )

    assert not result.is_valid


def test_failure_reason_present() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.FAILURE,
        ),
    )

    assert result.reason != ""


def test_failure_with_high_score_is_invalid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.FAILURE,
            score=1.0,
        ),
    )

    assert not result.is_valid


# --------------------------------------------------
# PARTIAL
# --------------------------------------------------


def test_partial_above_threshold_is_valid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.PARTIAL,
            score=0.90,
        ),
    )

    assert result.is_valid


def test_partial_below_threshold_is_invalid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.PARTIAL,
            score=0.40,
        ),
    )

    assert not result.is_valid


def test_partial_equal_threshold_is_valid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.PARTIAL,
            score=0.70,
        ),
    )

    assert result.is_valid


def test_partial_score_zero_is_invalid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.PARTIAL,
            score=0.0,
        ),
    )

    assert not result.is_valid


def test_partial_score_one_is_valid() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(
            status=OutcomeStatus.PARTIAL,
            score=1.0,
        ),
    )

    assert result.is_valid


# --------------------------------------------------
# Convenience helpers
# --------------------------------------------------


def test_is_valid_returns_true() -> None:
    validator = Validator()

    assert validator.is_valid(make_outcome())


def test_is_valid_returns_false() -> None:
    validator = Validator()

    assert not validator.is_valid(
        make_outcome(
            status=OutcomeStatus.FAILURE,
        ),
    )


def test_is_invalid_returns_true() -> None:
    validator = Validator()

    assert validator.is_invalid(
        make_outcome(
            status=OutcomeStatus.FAILURE,
        ),
    )


def test_is_invalid_returns_false() -> None:
    validator = Validator()

    assert not validator.is_invalid(make_outcome())


# --------------------------------------------------
# Data preservation
# --------------------------------------------------


def test_metrics_preserved() -> None:
    validator = Validator()

    outcome = make_outcome(
        metrics={
            "latency": 120.0,
            "accuracy": 0.95,
        },
    )

    result = validator.validate(outcome)

    assert result.outcome.metrics["latency"] == 120.0
    assert result.outcome.metrics["accuracy"] == 0.95


def test_description_preserved() -> None:
    validator = Validator()

    outcome = make_outcome(
        description="Completed successfully.",
    )

    result = validator.validate(outcome)

    assert result.outcome.description == "Completed successfully."


def test_empty_metrics_supported() -> None:
    validator = Validator()

    result = validator.validate(
        make_outcome(metrics={}),
    )

    assert result.outcome.metrics == {}


# --------------------------------------------------
# Stateless behavior
# --------------------------------------------------


def test_multiple_validations() -> None:
    validator = Validator()

    first = validator.validate(make_outcome())

    second = validator.validate(make_outcome())

    assert first.is_valid
    assert second.is_valid


def test_validator_is_stateless() -> None:
    validator = Validator()

    validator.validate(make_outcome())

    validator.validate(
        make_outcome(
            status=OutcomeStatus.FAILURE,
        ),
    )

    result = validator.validate(make_outcome())

    assert result.is_valid