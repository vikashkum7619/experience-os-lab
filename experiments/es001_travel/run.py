from __future__ import annotations

from dataclasses import dataclass

from experience_os.experience import ExperienceBuilder
from experience_os.models import (
    ApplicabilityStatus,
    Decision,
    Experience,
    Outcome,
    OutcomeStatus,
)
from experience_os.planner import (
    ExperienceInformedPlanner,
)
from experience_os.recall import (
    ExperienceApplicability,
    ExperienceRecall,
    ExperienceStore,
)

from .scenarios import (
    TravelScenario,
    create_test_scenarios,
    create_training_scenarios,
)


@dataclass(frozen=True)
class ExperimentResult:
    """Result from evaluating one test scenario."""

    scenario_number: int
    success: bool
    score: float
    used_experience: bool
    applicability: str
    candidate_count: int
    applicable_count: int
    selected_experience_id: str | None


def choose_flight_without_experience(
    scenario: TravelScenario,
) -> str:
    """Baseline strategy: choose the lowest advertised ticket price."""

    return min(
        scenario.options,
        key=lambda option: option.ticket_price,
    ).name


def choose_flight_with_experience(
    scenario: TravelScenario,
    decision: Decision,
) -> str:
    """Execute the decision produced by Experience OS."""

    if decision.description == "Check baggage before comparing price":
        return min(
            scenario.options,
            key=lambda option: option.ticket_price
            + option.baggage_cost,
        ).name

    return min(
        scenario.options,
        key=lambda option: option.ticket_price,
    ).name


def evaluate_choice(
    scenario: TravelScenario,
    selected_option: str,
    *,
    scenario_number: int,
    used_experience: bool,
    applicability: str,
    candidate_count: int,
    applicable_count: int,
    selected_experience_id: str | None,
) -> ExperimentResult:
    """Evaluate a selected flight against the known optimal option."""

    success = selected_option == scenario.optimal_option

    return ExperimentResult(
        scenario_number=scenario_number,
        success=success,
        score=1.0 if success else 0.0,
        used_experience=used_experience,
        applicability=applicability,
        candidate_count=candidate_count,
        applicable_count=applicable_count,
        selected_experience_id=selected_experience_id,
    )


def expert_training_decision(
    scenario: TravelScenario,
) -> Decision:
    """
    Controlled expert policy used to generate training experience.

    This policy is outside Experience OS. It represents the successful
    execution that ExperienceBuilder will convert into experience.
    """

    context = scenario.task.context

    if (
        context.get("traveler_type") == "family"
        and context.get("checked_baggage") is True
    ):
        return Decision(
            description="Check baggage before comparing price",
            rationale=(
                "Checked baggage can change the total trip cost, "
                "so baggage cost must be considered."
            ),
        )

    if (
        context.get("traveler_type") == "family"
        and context.get("checked_baggage") is False
    ):
        return Decision(
            description="Compare ticket price",
            rationale=(
                "No checked baggage is required, so compare "
                "the advertised ticket price."
            ),
        )

    if context.get("traveler_type") == "business":
        return Decision(
            description="Check baggage before comparing price",
            rationale=(
                "Business travel with checked baggage can change "
                "the total trip cost."
            ),
        )

    return Decision(
        description="Check refundability",
        rationale=(
            "International family travel may require stronger "
            "attention to refundability."
        ),
    )


def execute_training_decision(
    scenario: TravelScenario,
    decision: Decision,
) -> str:
    """Execute the controlled training decision."""

    if decision.description == "Check baggage before comparing price":
        return min(
            scenario.options,
            key=lambda option: (
                option.ticket_price + option.baggage_cost
            ),
        ).name

    return min(
        scenario.options,
        key=lambda option: option.ticket_price,
    ).name


def build_training_experience() -> ExperienceStore:
    """
    Generate experiences from successful training executions.

    Experience objects are produced by ExperienceBuilder and are not
    manually inserted into the store.
    """

    store = ExperienceStore()
    builder = ExperienceBuilder()

    for scenario in create_training_scenarios():
        decision = expert_training_decision(scenario)
        selected = execute_training_decision(
            scenario,
            decision,
        )

        if selected != scenario.optimal_option:
            continue

        outcome = Outcome(
            status=OutcomeStatus.SUCCESS,
            score=1.0,
            metrics={"training_success": 1.0},
            description="Training execution selected the optimal flight.",
        )

        experience = builder.build(
            scenario.task,
            decision,
            outcome,
        )

        if experience is not None:
            store.add(experience)

    return store


def run_baseline(
    scenarios: list[TravelScenario],
) -> list[ExperimentResult]:
    """Run the baseline strategy on the test scenarios."""

    results: list[ExperimentResult] = []

    for index, scenario in enumerate(
        scenarios,
        start=1,
    ):
        selected = choose_flight_without_experience(scenario)

        results.append(
            evaluate_choice(
                scenario,
                selected,
                scenario_number=index,
                used_experience=False,
                applicability="baseline",
                candidate_count=0,
                applicable_count=0,
                selected_experience_id=None,
            )
        )

    return results


def classify_applicability(
    experiences: list[Experience],
    task: object,
) -> tuple[
    list[Experience],
    list[tuple[Experience, str]],
]:
    """
    Classify recalled experiences independently.

    Returns applicable experiences and all classifications.

    The task argument is typed as object here only because the experiment
    passes the task directly from the scenario. The actual evaluator
    accepts a Task instance.
    """

    applicability_evaluator = ExperienceApplicability()

    classifications: list[tuple[Experience, str]] = []
    applicable: list[Experience] = []

    for experience in experiences:
        result = applicability_evaluator.evaluate(
            experience,
            task,  # type: ignore[arg-type]
        )

        classifications.append(
            (
                experience,
                result.status.value,
            )
        )

        if result.status == ApplicabilityStatus.APPLY:
            applicable.append(experience)

    return applicable, classifications


def run_experience(
    scenarios: list[TravelScenario],
    store: ExperienceStore,
) -> list[ExperimentResult]:
    """Run the Experience OS strategy with detailed diagnostics."""

    recall = ExperienceRecall(store)
    planner = ExperienceInformedPlanner(recall)

    results: list[ExperimentResult] = []

    for index, scenario in enumerate(
        scenarios,
        start=1,
    ):
        candidates = recall.recall(scenario.task)

        applicable, classifications = classify_applicability(
            candidates,
            scenario.task,
        )

        planner_result = planner.plan(scenario.task)

        used_experience = (
            planner_result.used_experience is not None
        )

        selected_experience_id = (
            str(planner_result.used_experience.id)
            if planner_result.used_experience is not None
            else None
        )

        if used_experience:
            applicability = "apply"
        elif any(
            status == ApplicabilityStatus.UNCERTAIN.value
            for _, status in classifications
        ):
            applicability = "uncertain"
        elif candidates:
            applicability = "reject"
        else:
            applicability = "no_candidate"

        selected = choose_flight_with_experience(
            scenario,
            planner_result.decision,
        )

        result = evaluate_choice(
            scenario,
            selected,
            scenario_number=index,
            used_experience=used_experience,
            applicability=applicability,
            candidate_count=len(candidates),
            applicable_count=len(applicable),
            selected_experience_id=selected_experience_id,
        )

        results.append(result)

        print(
            f"Scenario {index:02d} | "
            f"candidates={len(candidates)} | "
            f"applicable={len(applicable)} | "
            f"selection={selected_experience_id or 'baseline'} | "
            f"status={applicability} | "
            f"success={'YES' if result.success else 'NO'}"
        )

    return results


def success_rate(
    results: list[ExperimentResult],
) -> float:
    """Calculate success rate."""

    if not results:
        return 0.0

    return sum(
        result.success
        for result in results
    ) / len(results)


def count_status(
    results: list[ExperimentResult],
    status: str,
) -> int:
    """Count results by applicability status."""

    return sum(
        result.applicability == status
        for result in results
    )


def main() -> None:
    """Run D9.2 multi-experience benchmark."""

    training_scenarios = create_training_scenarios()
    test_scenarios = create_test_scenarios()

    experience_store = build_training_experience()

    print()
    print("Experience OS — ES001.2")
    print("======================")
    print(
        f"Training scenarios: "
        f"{len(training_scenarios)}"
    )
    print(
        f"Generated experiences: "
        f"{len(experience_store.all())}"
    )
    print(
        f"Test scenarios: "
        f"{len(test_scenarios)}"
    )

    print()
    print("GENERATED EXPERIENCES")

    for index, experience in enumerate(
        experience_store.all(),
        start=1,
    ):
        print(
            f"  E{index}: "
            f"conditions={experience.conditions} | "
            f"decision={experience.decision_pattern[0]}"
        )

    print()
    print("SCENARIO ANALYSIS")
    print("------------------")

    baseline_results = run_baseline(
        test_scenarios,
    )

    experience_results = run_experience(
        test_scenarios,
        experience_store,
    )

    baseline_rate = success_rate(
        baseline_results,
    )

    experience_rate = success_rate(
        experience_results,
    )

    reused_count = sum(
        result.used_experience
        for result in experience_results
    )

    applicable_count = sum(
        result.applicable_count
        for result in experience_results
    )

    correct_reuse_count = sum(
        result.success and result.used_experience
        for result in experience_results
    )

    print()
    print("RESULTS")
    print("-------")

    print()
    print("BASELINE")
    print(
        f"  Success rate: "
        f"{baseline_rate:.0%}"
    )

    print()
    print("EXPERIENCE OS")
    print(
        f"  Success rate: "
        f"{experience_rate:.0%}"
    )
    print(
        f"  Experience reused: "
        f"{reused_count}/{len(experience_results)}"
    )
    print(
        f"  Applicable experiences encountered: "
        f"{applicable_count}"
    )
    print(
        f"  Correct reuse: "
        f"{correct_reuse_count}"
    )

    print()
    print("APPLICABILITY")
    print(
        f"  APPLY: "
        f"{count_status(experience_results, 'apply')}"
    )
    print(
        f"  UNCERTAIN: "
        f"{count_status(experience_results, 'uncertain')}"
    )
    print(
        f"  REJECT: "
        f"{count_status(experience_results, 'reject')}"
    )
    print(
        f"  NO CANDIDATE: "
        f"{count_status(experience_results, 'no_candidate')}"
    )

    print()
    print("EXPERIENCE SELECTION")
    print(
        f"  Selection accuracy: "
        f"{correct_reuse_count / reused_count:.0%}"
        if reused_count
        else "  Selection accuracy: N/A"
    )

    print()
    print("EXPERIENCE LIFT")
    print(
        f"  Quality improvement: "
        f"{experience_rate - baseline_rate:+.0%}"
    )


if __name__ == "__main__":
    main()