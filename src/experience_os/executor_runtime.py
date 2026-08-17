from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from experience_os.experience_pipeline import (
    ExperiencePipeline,
    PipelineResult,
)
from experience_os.models import (
    Outcome,
    Task,
)
from experience_os.planner import (
    ExperienceInformedPlanner,
    PlannerResult,
)
from experience_os.tool_executor import (
    ToolExecutionResult,
    ToolExecutor,
)
from experience_os.working_memory import WorkingMemory


# ---------------------------------------------------------
# Runtime Result
# ---------------------------------------------------------


@dataclass(slots=True)
class RuntimeResult:
    """
    Result of a complete runtime execution.
    """

    planner_result: PlannerResult
    pipeline_result: PipelineResult
    tool_results: list[ToolExecutionResult] = field(
        default_factory=list,
    )


# ---------------------------------------------------------
# Executor Runtime
# ---------------------------------------------------------


class ExecutorRuntime:
    """
    Coordinates execution of the complete Experience OS runtime.

    Responsibilities
    ----------------
    1. Ask planner for a decision
    2. Execute tools (if requested)
    3. Update working memory
    4. Execute learning pipeline
    5. Return runtime result

    Future versions may support:
        - Multi-step planning
        - Autonomous tool selection
        - Retry loops
        - Streaming execution
        - Human approval
    """

    def __init__(
        self,
        *,
        planner: ExperienceInformedPlanner,
        tool_executor: ToolExecutor,
        working_memory: WorkingMemory,
        pipeline: ExperiencePipeline,
    ) -> None:

        self._planner = planner
        self._tool_executor = tool_executor
        self._working_memory = working_memory
        self._pipeline = pipeline

    # -----------------------------------------------------
    # Execute
    # -----------------------------------------------------

    def run(
        self,
        *,
        task: Task,
        outcome: Outcome,
    ) -> RuntimeResult:
        """
        Execute one complete runtime cycle.
        """

        # ---------------------------------------------
        # Planning
        # ---------------------------------------------

        planner_result = self._planner.plan(task)

        tool_results: list[ToolExecutionResult] = []

        # ---------------------------------------------
        # Tool Execution (simple convention)
        # ---------------------------------------------
        #
        # If the planner returns a decision whose
        # description matches a registered tool,
        # execute it.
        #

        tool_name = planner_result.decision.description

        if self._tool_executor.can_execute(tool_name):

            result = self._tool_executor.execute(
                tool_name,
            )

            tool_results.append(result)

            if result.success:

                self._working_memory.add_note(
                    f"{tool_name}: {result.output}"
                )

            else:

                self._working_memory.add_note(
                    f"{tool_name} failed: {result.error}"
                )

        # ---------------------------------------------
        # Learn
        # ---------------------------------------------

        pipeline_result = self._pipeline.run(
            task=task,
            outcome=outcome,
        )

        return RuntimeResult(
            planner_result=planner_result,
            pipeline_result=pipeline_result,
            tool_results=tool_results,
        )

    # -----------------------------------------------------
    # Convenience
    # -----------------------------------------------------

    def available_tools(self) -> list[str]:
        """
        Return names of executable tools.
        """

        return self._tool_executor.available_tools()

    def clear_working_memory(self) -> None:
        """
        Clear runtime working memory.
        """

        self._working_memory.clear()

    @property
    def working_memory(self) -> WorkingMemory:
        """
        Access runtime working memory.
        """

        return self._working_memory