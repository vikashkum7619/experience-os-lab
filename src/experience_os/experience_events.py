from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(UTC)


class ExperienceEventType(StrEnum):
    """Supported Experience OS events."""

    EXPERIENCE_CREATED = "experience_created"
    EXPERIENCE_UPDATED = "experience_updated"
    EXPERIENCE_REMOVED = "experience_removed"

    EXPERIENCE_RECALLED = "experience_recalled"
    EXPERIENCE_REUSED = "experience_reused"

    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"

    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"

    LEARNING_COMPLETED = "learning_completed"


@dataclass(slots=True)
class ExperienceEvent:
    """
    Immutable event emitted by Experience OS.
    """

    id: UUID = field(default_factory=uuid4)
    event_type: ExperienceEventType = ExperienceEventType.EXPERIENCE_CREATED
    timestamp: datetime = field(default_factory=utc_now)

    experience_id: UUID | None = None
    task_id: UUID | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


class ExperienceEventBus:
    """
    Simple in-memory event bus.

    Gen-1
    -----
    Stores emitted events.

    Gen-2
    -----
    Will support subscriptions.

    Gen-3
    -----
    Event streaming (Kafka, Redis, etc.)
    """

    def __init__(self) -> None:
        self._events: list[ExperienceEvent] = []

    @property
    def events(self) -> list[ExperienceEvent]:
        return list(self._events)

    def publish(
        self,
        event: ExperienceEvent,
    ) -> None:
        """Publish an event."""
        self._events.append(event)

    def count(self) -> int:
        """Return number of published events."""
        return len(self._events)

    def latest(self) -> ExperienceEvent | None:
        """Return the most recent event."""
        if not self._events:
            return None
        return self._events[-1]

    def clear(self) -> None:
        """Remove all events."""
        self._events.clear()

    def by_type(
        self,
        event_type: ExperienceEventType,
    ) -> list[ExperienceEvent]:
        """Return events of a specific type."""
        return [
            event
            for event in self._events
            if event.event_type == event_type
        ]

    def by_experience(
        self,
        experience_id: UUID,
    ) -> list[ExperienceEvent]:
        """Return events for an experience."""
        return [
            event
            for event in self._events
            if event.experience_id == experience_id
        ]

    def by_task(
        self,
        task_id: UUID,
    ) -> list[ExperienceEvent]:
        """Return events for a task."""
        return [
            event
            for event in self._events
            if event.task_id == task_id
        ]