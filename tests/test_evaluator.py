from experience_os.evaluator import DeterministicEvaluator
from experience_os.models import (
    Decision,
    OutcomeStatus,
    Task,
)


def test_family_total_cost_decision_succeeds() -> None:
    evaluator = DeterministicEvaluator()

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
        constraints={"max_budget": 80000},
    )

    decision = Decision(
        description="Compare total trip cost",
        rationale="Family travel may include additional costs.",
    )

    outcome = evaluator.evaluate(task, decision)

    assert outcome.status == OutcomeStatus.SUCCESS
    assert outcome.score == 1.0
    assert outcome.metrics["decision_quality"] == 1.0


def test_family_ticket_price_only_decision_fails() -> None:
    evaluator = DeterministicEvaluator()

    task = Task(
        goal="Book an international flight",
        context={"traveler_type": "family"},
        constraints={"max_budget": 80000},
    )

    decision = Decision(
        description="Select the cheapest ticket",
        rationale="Choose the lowest advertised ticket price.",
    )

    outcome = evaluator.evaluate(task, decision)

    assert outcome.status == OutcomeStatus.FAILURE
    assert outcome.score == 0.0


def test_business_task_constraint_decision_succeeds() -> None:
    evaluator = DeterministicEvaluator()

    task = Task(
        goal="Book a business flight",
        context={"traveler_type": "business"},
        constraints={"max_budget": 50000},
    )

    decision = Decision(
        description="Compare available options against task constraints",
        rationale="The budget constraint should influence the decision.",
    )

    outcome = evaluator.evaluate(task, decision)

    assert outcome.status == OutcomeStatus.SUCCESS
    assert outcome.score == 0.8


def test_unknown_decision_produces_partial_outcome() -> None:
    evaluator = DeterministicEvaluator()

    task = Task(
        goal="Book a business flight",
        context={"traveler_type": "business"},
    )

    decision = Decision(
        description="Choose the first available option",
        rationale="The first available option may be acceptable.",
    )

    outcome = evaluator.evaluate(task, decision)

    assert outcome.status == OutcomeStatus.PARTIAL
    assert outcome.score == 0.5