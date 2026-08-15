from experience_os.trust import (
    EvidenceAccumulator,
    ExperienceEvidence,
    TrustCalculator,
)


def test_new_evidence_has_zero_trust() -> None:
    evidence = ExperienceEvidence()

    calculator = TrustCalculator()

    assert calculator.calculate(evidence) == 0.0


def test_success_updates_statistics() -> None:
    evidence = ExperienceEvidence()

    evidence.record(True)

    assert evidence.executions == 1
    assert evidence.successes == 1
    assert evidence.failures == 0
    assert evidence.success_rate == 1.0


def test_failure_updates_statistics() -> None:
    evidence = ExperienceEvidence()

    evidence.record(False)

    assert evidence.executions == 1
    assert evidence.successes == 0
    assert evidence.failures == 1
    assert evidence.success_rate == 0.0


def test_mixed_results() -> None:
    evidence = ExperienceEvidence()

    evidence.record(True)
    evidence.record(True)
    evidence.record(False)
    evidence.record(True)

    assert evidence.executions == 4
    assert evidence.successes == 3
    assert evidence.failures == 1
    assert evidence.success_rate == 0.75


def test_trust_calculator() -> None:
    evidence = ExperienceEvidence()

    for _ in range(9):
        evidence.record(True)

    evidence.record(False)

    calculator = TrustCalculator()

    assert calculator.calculate(evidence) == 0.9


def test_accumulator_records_success() -> None:
    evidence = ExperienceEvidence()

    accumulator = EvidenceAccumulator()

    accumulator.accumulate(
        evidence,
        success=True,
    )

    assert evidence.executions == 1
    assert evidence.successes == 1
    assert evidence.failures == 0


def test_accumulator_records_failure() -> None:
    evidence = ExperienceEvidence()

    accumulator = EvidenceAccumulator()

    accumulator.accumulate(
        evidence,
        success=False,
    )

    assert evidence.executions == 1
    assert evidence.successes == 0
    assert evidence.failures == 1


def test_accumulator_multiple_updates() -> None:
    evidence = ExperienceEvidence()

    accumulator = EvidenceAccumulator()

    accumulator.accumulate(evidence, success=True)
    accumulator.accumulate(evidence, success=True)
    accumulator.accumulate(evidence, success=False)

    assert evidence.executions == 3
    assert evidence.successes == 2
    assert evidence.failures == 1
    assert evidence.success_rate == 2 / 3