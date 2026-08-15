from __future__ import annotations

from experience_os.models import Experience
from experience_os.recall import ExperienceStore
from experience_os.trust import ExperienceEvidence, TrustCalculator


class ExperienceConsolidator:
    """
    Consolidates duplicate experiences into a single stronger experience.

    Duplicate experiences are those having identical conditions and
    identical decision patterns.

    Rather than storing many copies of the same experience, evidence is
    accumulated into the existing experience and confidence is updated.
    """

    def __init__(
        self,
        store: ExperienceStore,
        trust_calculator: TrustCalculator | None = None,
    ) -> None:
        self._store = store
        self._trust = trust_calculator or TrustCalculator()

    def consolidate(
        self,
        experience: Experience,
    ) -> Experience:
        """
        Store a new experience or merge it into an existing one.

        Returns the stored experience.
        """

        existing = self.find_duplicate(experience)

        if existing is None:
            self._store.add(experience)
            return experience

        self.merge(existing, experience)
        return existing

    def find_duplicate(
        self,
        experience: Experience,
    ) -> Experience | None:
        """
        Search for an equivalent experience.

        Two experiences are considered duplicates when both the
        conditions and decision pattern are identical.
        """

        for candidate in self._store.all():

            if (
                candidate.conditions == experience.conditions
                and candidate.decision_pattern
                == experience.decision_pattern
            ):
                return candidate

        return None

    def merge(
        self,
        existing: Experience,
        new: Experience,
    ) -> None:
        """
        Merge evidence from a new experience into an existing one.
        """

        evidence = ExperienceEvidence(
            executions=existing.execution_count,
            successes=existing.successful_executions,
            failures=(
                existing.execution_count
                - existing.successful_executions
            ),
        )

        additional_successes = new.successful_executions
        additional_failures = (
            new.execution_count
            - new.successful_executions
        )

        evidence.executions += new.execution_count
        evidence.successes += additional_successes
        evidence.failures += additional_failures

        existing.execution_count = evidence.executions
        existing.successful_executions = evidence.successes
        existing.confidence = self._trust.calculate(evidence)

        # Replace the decision pattern only if the new experience has
        # stronger confidence.
        if new.confidence > existing.confidence:
            existing.decision_pattern = list(
                new.decision_pattern
            )