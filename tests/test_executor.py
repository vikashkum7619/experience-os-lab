from __future__ import annotations

from experience_os.executor import (
    ExecutionResult,
    Executor,
)
from experience_os.models import Task


def make_task() -> Task:
    return Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
        },
    )


def test_executor_creates_default_instance() -> None:
    executor = Executor()

    assert executor is not None


def test_execute_returns_execution_result() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert isinstance(
        result,
        ExecutionResult,
    )


def test_result_contains_original_task() -> None:
    executor = Executor()

    task = make_task()

    result = executor.execute(task)

    assert result.task == task


def test_result_contains_outcome() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert result.outcome is not None


def test_result_success_is_true() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert result.success is True


def test_result_has_started_time() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert result.started_at is not None


def test_result_has_finished_time() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert result.finished_at is not None


def test_duration_is_non_negative() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert result.duration >= 0.0


def test_simulate_returns_execution_result() -> None:
    executor = Executor()

    result = executor.simulate(
        make_task(),
    )

    assert isinstance(
        result,
        ExecutionResult,
    )


def test_simulate_returns_success() -> None:
    executor = Executor()

    result = executor.simulate(
        make_task(),
    )

    assert result.success is True


def test_simulate_preserves_task() -> None:
    executor = Executor()

    task = make_task()

    result = executor.simulate(task)

    assert result.task == task


def test_explain_returns_dictionary() -> None:
    executor = Executor()

    explanation = executor.explain()

    assert isinstance(
        explanation,
        dict,
    )


def test_explain_contains_executor_name() -> None:
    executor = Executor()

    explanation = executor.explain()

    assert "executor" in explanation


def test_explain_contains_version() -> None:
    executor = Executor()

    explanation = executor.explain()

    assert "version" in explanation


def test_reset_does_not_fail() -> None:
    executor = Executor()

    executor.reset()


def test_reset_preserves_functionality() -> None:
    executor = Executor()

    executor.reset()

    result = executor.execute(
        make_task(),
    )

    assert result.success is True


def test_multiple_executions_are_supported() -> None:
    executor = Executor()

    first = executor.execute(
        make_task(),
    )

    second = executor.execute(
        make_task(),
    )

    assert first.success
    assert second.success


def test_execution_result_contains_outcome_description() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert result.outcome.description != ""


def test_execution_result_contains_score() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert 0.0 <= result.outcome.score <= 1.0


def test_execution_result_contains_metrics() -> None:
    executor = Executor()

    result = executor.execute(
        make_task(),
    )

    assert isinstance(
        result.outcome.metrics,
        dict,
    )