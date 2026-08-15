from __future__ import annotations

from uuid import uuid4

from experience_os.experience_events import (
    ExperienceEvent,
    ExperienceEventBus,
    ExperienceEventType,
)


def test_event_has_id() -> None:
    event = ExperienceEvent()

    assert event.id is not None


def test_event_has_timestamp() -> None:
    event = ExperienceEvent()

    assert event.timestamp is not None


def test_default_event_type() -> None:
    event = ExperienceEvent()

    assert (
        event.event_type
        == ExperienceEventType.EXPERIENCE_CREATED
    )


def test_default_metadata_empty() -> None:
    event = ExperienceEvent()

    assert event.metadata == {}


def test_default_experience_id_none() -> None:
    event = ExperienceEvent()

    assert event.experience_id is None


def test_default_task_id_none() -> None:
    event = ExperienceEvent()

    assert event.task_id is None


def test_event_bus_initially_empty() -> None:
    bus = ExperienceEventBus()

    assert bus.count() == 0


def test_latest_empty_returns_none() -> None:
    bus = ExperienceEventBus()

    assert bus.latest() is None


def test_publish_adds_event() -> None:
    bus = ExperienceEventBus()

    event = ExperienceEvent()

    bus.publish(event)

    assert bus.count() == 1


def test_latest_returns_last_event() -> None:
    bus = ExperienceEventBus()

    first = ExperienceEvent()
    second = ExperienceEvent()

    bus.publish(first)
    bus.publish(second)

    assert bus.latest() == second


def test_events_property_returns_copy() -> None:
    bus = ExperienceEventBus()

    event = ExperienceEvent()

    bus.publish(event)

    events = bus.events

    events.clear()

    assert bus.count() == 1


def test_clear_removes_all_events() -> None:
    bus = ExperienceEventBus()

    bus.publish(ExperienceEvent())
    bus.publish(ExperienceEvent())

    bus.clear()

    assert bus.count() == 0


def test_by_type_returns_matching_events() -> None:
    bus = ExperienceEventBus()

    created = ExperienceEvent(
        event_type=ExperienceEventType.EXPERIENCE_CREATED
    )

    updated = ExperienceEvent(
        event_type=ExperienceEventType.EXPERIENCE_UPDATED
    )

    bus.publish(created)
    bus.publish(updated)

    events = bus.by_type(
        ExperienceEventType.EXPERIENCE_CREATED
    )

    assert len(events) == 1
    assert events[0] == created


def test_by_type_empty_when_missing() -> None:
    bus = ExperienceEventBus()

    events = bus.by_type(
        ExperienceEventType.LEARNING_COMPLETED
    )

    assert events == []


def test_by_experience_returns_matching() -> None:
    bus = ExperienceEventBus()

    exp_id = uuid4()

    event = ExperienceEvent(
        experience_id=exp_id,
    )

    bus.publish(event)

    result = bus.by_experience(exp_id)

    assert len(result) == 1
    assert result[0] == event


def test_by_experience_returns_empty() -> None:
    bus = ExperienceEventBus()

    assert bus.by_experience(uuid4()) == []


def test_by_task_returns_matching() -> None:
    bus = ExperienceEventBus()

    task_id = uuid4()

    event = ExperienceEvent(
        task_id=task_id,
    )

    bus.publish(event)

    result = bus.by_task(task_id)

    assert len(result) == 1
    assert result[0] == event


def test_by_task_returns_empty() -> None:
    bus = ExperienceEventBus()

    assert bus.by_task(uuid4()) == []


def test_multiple_events_count() -> None:
    bus = ExperienceEventBus()

    for _ in range(5):
        bus.publish(ExperienceEvent())

    assert bus.count() == 5


def test_latest_after_clear_returns_none() -> None:
    bus = ExperienceEventBus()

    bus.publish(ExperienceEvent())

    bus.clear()

    assert bus.latest() is None


def test_publish_preserves_order() -> None:
    bus = ExperienceEventBus()

    first = ExperienceEvent()
    second = ExperienceEvent()

    bus.publish(first)
    bus.publish(second)

    assert bus.events[0] == first
    assert bus.events[1] == second


def test_events_returns_new_list() -> None:
    bus = ExperienceEventBus()

    bus.publish(ExperienceEvent())

    assert bus.events is not bus.events


def test_multiple_filters_work_independently() -> None:
    bus = ExperienceEventBus()

    exp_id = uuid4()
    task_id = uuid4()

    event = ExperienceEvent(
        event_type=ExperienceEventType.EXECUTION_COMPLETED,
        experience_id=exp_id,
        task_id=task_id,
    )

    bus.publish(event)

    assert len(
        bus.by_type(
            ExperienceEventType.EXECUTION_COMPLETED
        )
    ) == 1

    assert len(
        bus.by_experience(exp_id)
    ) == 1

    assert len(
        bus.by_task(task_id)
    ) == 1