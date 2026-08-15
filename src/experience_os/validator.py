from __future__ import annotations

from dataclasses import dataclass

from experience_os.models import (
    Outcome,
    OutcomeStatus,
)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Result of validating an execution outcome.

    Attributes
    ----------
    valid
        Whether the execution is considered valid.

    score
        Validation score.

    reason
        Human-readable explanation.

    outcome
        Original execution outcome.
    """

    valid: bool
    score: float
    reason: str
    outcome: Outcome

    @property
    def is_valid(self) -> bool:
        """
        Backward-compatible alias.
        """
        return self.valid


class Validator:
    """
    Validate execution outcomes.

    Responsibilities
    ----------------
    - Determine whether an execution is acceptable.
    - Produce a validation result.

    Does NOT
    --------
    - Learn
    - Store experiences
    - Execute tasks
    - Plan
    """

    def __init__(
        self,
        minimum_score: float = 0.70,
    ) -> None:
        self._minimum_score = minimum_score

    @property
    def minimum_score(self) -> float:
        """
        Minimum score required for PARTIAL outcomes.
        """
        return self._minimum_score

    def validate(
        self,
        outcome: Outcome,
    ) -> ValidationResult:
        """
        Validate an execution outcome.
        """

        if outcome.status == OutcomeStatus.SUCCESS:
            return ValidationResult(
                valid=True,
                score=outcome.score,
                reason="Execution completed successfully.",
                outcome=outcome,
            )

        if outcome.status == OutcomeStatus.FAILURE:
            return ValidationResult(
                valid=False,
                score=outcome.score,
                reason="Execution failed.",
                outcome=outcome,
            )

        # PARTIAL outcome

        if outcome.score >= self._minimum_score:
            return ValidationResult(
                valid=True,
                score=outcome.score,
                reason=(
                    "Partial execution exceeded the minimum "
                    "acceptable score."
                ),
                outcome=outcome,
            )

        return ValidationResult(
            valid=False,
            score=outcome.score,
            reason=(
                "Partial execution did not meet the minimum "
                "acceptable score."
            ),
            outcome=outcome,
        )

    def is_valid(
        self,
        outcome: Outcome,
    ) -> bool:
        """
        Convenience helper.
        """
        return self.validate(outcome).valid

    def is_invalid(
        self,
        outcome: Outcome,
    ) -> bool:
        """
        Convenience helper.
        """
        return not self.is_valid(outcome)