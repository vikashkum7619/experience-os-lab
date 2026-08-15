from __future__ import annotations

from experience_os.execution_trace import (
    ExecutionTrace,
    TraceStep,
)
from experience_os.models import OutcomeStatus


def make_trace() -> ExecutionTrace:
    return ExecutionTrace(
        task_goal="Book a family flight",
        task_context={
            "traveler_type": "family",
        },
    )


def test_new_trace_is_empty() -> None:
    trace = make_trace()

    assert trace.step_count == 0
    assert trace.steps == []
    assert trace.finished_at is None


def test_add_step() -> None:
    trace = make_trace()

    step = TraceStep(
        name="Search Flights",
    )

    trace.add_step(step)

    assert trace.step_count == 1
    assert trace.steps[0] == step


def test_record_creates_step() -> None:
    trace = make_trace()

    step = trace.record(
        name="Search Flights",
    )

    assert step.name == "Search Flights"
    assert trace.step_count == 1


def test_record_preserves_input() -> None:
    trace = make_trace()

    step = trace.record(
        name="Planner",
        input={
            "goal": "flight",
        },
    )

    assert step.input["goal"] == "flight"


def test_record_preserves_output() -> None:
    trace = make_trace()

    step = trace.record(
        name="Planner",
        output={
            "decision": "search",
        },
    )

    assert step.output["decision"] == "search"


def test_record_preserves_metadata() -> None:
    trace = make_trace()

    step = trace.record(
        name="Planner",
        metadata={
            "model": "gpt",
        },
    )

    assert step.metadata["model"] == "gpt"


def test_finish_sets_status() -> None:
    trace = make_trace()

    trace.finish(
        status=OutcomeStatus.SUCCESS,
        score=0.95,
    )

    assert trace.status == OutcomeStatus.SUCCESS


def test_finish_sets_score() -> None:
    trace = make_trace()

    trace.finish(
        status=OutcomeStatus.SUCCESS,
        score=0.83,
    )

    assert trace.score == 0.83


def test_finish_sets_finished_time() -> None:
    trace = make_trace()

    trace.finish(
        status=OutcomeStatus.SUCCESS,
        score=1.0,
    )

    assert trace.finished_at is not None


def test_successful_property() -> None:
    trace = make_trace()

    trace.finish(
        status=OutcomeStatus.SUCCESS,
        score=1.0,
    )

    assert trace.successful


def test_failed_trace_is_not_successful() -> None:
    trace = make_trace()

    trace.finish(
        status=OutcomeStatus.FAILURE,
        score=0.2,
    )

    assert not trace.successful


def test_duration_exists_after_finish() -> None:
    trace = make_trace()

    trace.finish(
        status=OutcomeStatus.SUCCESS,
        score=1.0,
    )

    assert trace.duration_seconds is not None
    assert trace.duration_seconds >= 0


def test_duration_none_before_finish() -> None:
    trace = make_trace()

    assert trace.duration_seconds is None


def test_decision_pattern_returns_step_names() -> None:
    trace = make_trace()

    trace.record(name="Search")

    trace.record(name="Compare")

    trace.record(name="Book")

    assert trace.decision_pattern() == [
        "Search",
        "Compare",
        "Book",
    ]


def test_clear_resets_trace() -> None:
    trace = make_trace()

    trace.record(
        name="Search",
    )

    trace.finish(
        status=OutcomeStatus.SUCCESS,
        score=0.95,
    )

    trace.clear()

    assert trace.step_count == 0
    assert trace.finished_at is None
    assert trace.score == 1.0
    assert trace.status == OutcomeStatus.SUCCESS


def test_multiple_steps_are_recorded_in_order() -> None:
    trace = make_trace()

    trace.record(name="Step1")
    trace.record(name="Step2")
    trace.record(name="Step3")

    assert [
        step.name for step in trace.steps
    ] == [
        "Step1",
        "Step2",
        "Step3",
    ]