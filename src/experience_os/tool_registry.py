from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True, frozen=True)
class Tool:
    """
    Represents a callable tool that an agent can execute.
    """

    name: str
    description: str
    handler: Callable[..., Any]
    tags: list[str] = field(default_factory=list)


class ToolRegistry:
    """
    Registry of tools available to the agent.

    Responsibilities
    ----------------
    - Register tools
    - Remove tools
    - Lookup tools
    - List available tools
    - Execute is handled elsewhere (ToolExecutor)
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Raises
        ------
        ValueError
            If a tool with the same name already exists.
        """

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' already registered."
            )

        self._tools[tool.name] = tool

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a tool.

        Raises
        ------
        KeyError
            If the tool does not exist.
        """

        del self._tools[name]

    def clear(self) -> None:
        """
        Remove every registered tool.
        """

        self._tools.clear()

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Tool:
        """
        Retrieve a registered tool.
        """

        return self._tools[name]

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        True if the tool exists.
        """

        return name in self._tools

    # ---------------------------------------------------------
    # Listing
    # ---------------------------------------------------------

    def all(self) -> list[Tool]:
        """
        Return all registered tools.
        """

        return list(self._tools.values())

    def names(self) -> list[str]:
        """
        Return registered tool names.
        """

        return sorted(self._tools)

    def by_tag(
        self,
        tag: str,
    ) -> list[Tool]:
        """
        Return tools containing a tag.
        """

        return [
            tool
            for tool in self._tools.values()
            if tag in tool.tags
        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def size(self) -> int:
        """
        Number of registered tools.
        """

        return len(self._tools)

    def empty(self) -> bool:
        """
        True if no tools are registered.
        """

        return not self._tools