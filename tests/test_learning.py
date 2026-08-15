from experience_os.learning import ExperienceLearner
from experience_os.models import Experience


def build_experience() -> Experience:
    return Experience(
        conditions={"traveler_type": "family"},
        decision_pattern=["Check baggage"],
        execution_count=10,
        successful_executions=8,
        confidence=0.8,
    )


def test_success_updates_execution_count() -> None:
    learner = ExperienceLearner()
    experience = build_experience()

    learner.learn(
        experience,
        success=True,
    )

    assert experience.execution_count == 11
    assert experience.successful_executions == 9


def test_failure_updates_execution_count() -> None:
    learner = ExperienceLearner()
    experience = build_experience()

    learner.learn(
        experience,
        success=False,
    )

    assert experience.execution_count == 11
    assert experience.successful_executions == 8


def test_confidence_updates_after_success() -> None:
    learner = ExperienceLearner()
    experience = build_experience()

    learner.learn(
        experience,
        success=True,
    )

    assert abs(experience.confidence - (9 / 11)) < 1e-6


def test_confidence_updates_after_failure() -> None:
    learner = ExperienceLearner()
    experience = build_experience()

    learner.learn(
        experience,
        success=False,
    )

    assert abs(experience.confidence - (8 / 11)) < 1e-6


def test_learning_returns_same_object() -> None:
    learner = ExperienceLearner()
    experience = build_experience()

    updated = learner.learn(
        experience,
        success=True,
    )

    assert updated is experience