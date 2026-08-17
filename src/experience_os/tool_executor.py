from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from experience_os.tool_registry import Tool, ToolRegistry


# ---------------------------------------------------------
# Result
# ---------------------------------------------------------


@dataclass(slots=True, frozen=True)
class ToolExecutionResult:
    """
    Result returned after executing a tool.
    """

    tool_name: str
    success: bool
    output: Any
    error: str | None = None


# ---------------------------------------------------------
# Executor
# ---------------------------------------------------------


class ToolExecutor:
    """
    Executes registered tools.

    Responsibilities
    ----------------
    - Lookup tools
    - Execute handlers
    - Capture exceptions
    - Return structured execution results

    This class intentionally does not decide WHICH tool to run.
    """

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._registry = registry

    # -----------------------------------------------------
    # Execute by name
    # -----------------------------------------------------

    def execute(
        self,
        tool_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> ToolExecutionResult:
        """
        Execute a registered tool.

        Unknown tools raise KeyError.

        Tool exceptions are captured and returned.
        """

        tool = self._registry.get(tool_name)

        return self.execute_tool(
            tool,
            *args,
            **kwargs,
        )

    # -----------------------------------------------------
    # Execute Tool object
    # -----------------------------------------------------

    @staticmethod
    def execute_tool(
        tool: Tool,
        *args: Any,
        **kwargs: Any,
    ) -> ToolExecutionResult:
        """
        Execute a Tool instance.
        """

        try:

            result = tool.handler(
                *args,
                **kwargs,
            )

            return ToolExecutionResult(
                tool_name=tool.name,
                success=True,
                output=result,
                error=None,
            )

        except Exception as exc:

            return ToolExecutionResult(
                tool_name=tool.name,
                success=False,
                output=None,
                error=str(exc),
            )

    # -----------------------------------------------------
    # Convenience
    # -----------------------------------------------------

    def can_execute(
        self,
        tool_name: str,
    ) -> bool:
        """
        True if a tool exists.
        """

        return self._registry.exists(tool_name)

    def available_tools(self) -> list[str]:
        """
        Return registered tool names.
        """

        return self._registry.names()