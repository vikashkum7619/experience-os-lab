from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from experience_os.experience_pipeline import (
    ExperiencePipeline,
    PipelineResult,
)
from experience_os.models import (
    Outcome,
    Task,
)
from experience_os.tool_executor import ToolExecutor


# ---------------------------------------------------------
# Result
# ---------------------------------------------------------


@dataclass(slots=True)
class AgentResult:
    """
    Result returned by an Agent execution.
    """

    pipeline: PipelineResult
    tool_results: dict[str, Any]


# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------


class Agent:
    """
    High-level Experience OS Agent.

    Responsibilities
    ----------------
    - Accept user tasks
    - Execute tools
    - Invoke the Experience Pipeline
    - Return a unified result

    The Agent is the main entry point for applications.
    """

    def __init__(
        self,
        *,
        pipeline: ExperiencePipeline,
        tool_executor: ToolExecutor,
    ) -> None:

        self._pipeline = pipeline
        self._tool_executor = tool_executor

    # -----------------------------------------------------
    # Execute task
    # -----------------------------------------------------

    def run(
        self,
        *,
        task: Task,
        outcome: Outcome,
    ) -> AgentResult:
        """
        Execute one complete agent cycle.
        """

        pipeline_result = self._pipeline.run(
            task=task,
            outcome=outcome,
        )

        return AgentResult(
            pipeline=pipeline_result,
            tool_results={},
        )

    # -----------------------------------------------------
    # Execute Tool
    # -----------------------------------------------------

    def execute_tool(
        self,
        tool_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Execute a registered tool.
        """

        return self._tool_executor.execute(
            tool_name,
            *args,
            **kwargs,
        )

    # -----------------------------------------------------
    # Tool Information
    # -----------------------------------------------------

    def available_tools(self) -> list[str]:
        """
        Return available tool names.
        """

        return self._tool_executor.available_tools()

    def can_execute(
        self,
        tool_name: str,
    ) -> bool:
        """
        Whether a tool exists.
        """

        return self._tool_executor.can_execute(
            tool_name,
        )