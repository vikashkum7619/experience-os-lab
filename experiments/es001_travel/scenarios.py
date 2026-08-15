from __future__ import annotations

from dataclasses import dataclass

from experience_os.models import Task


@dataclass(frozen=True)
class FlightOption:
    """A flight option used by the controlled experiment."""

    name: str
    ticket_price: float
    baggage_cost: float


@dataclass(frozen=True)
class TravelScenario:
    """A controlled travel decision scenario."""

    task: Task
    options: tuple[FlightOption, ...]
    optimal_option: str


def create_training_scenarios() -> list[TravelScenario]:
    """
    Create training scenarios that generate four distinct experiences.

    E1:
        family + checked baggage
        -> check total trip cost

    E2:
        family + no checked baggage
        -> compare ticket price

    E3:
        business + checked baggage
        -> check total trip cost

    E4:
        international + family
        -> check refundability
    """

    return [
        TravelScenario(
            task=Task(
                goal="Choose the best family flight with baggage",
                context={
                    "traveler_type": "family",
                    "checked_baggage": True,
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 62000, 0),
                FlightOption("Flight B", 57000, 10000),
            ),
            optimal_option="Flight A",
        ),
        TravelScenario(
            task=Task(
                goal="Choose the best family flight without baggage",
                context={
                    "traveler_type": "family",
                    "checked_baggage": False,
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 62000, 5000),
                FlightOption("Flight B", 57000, 0),
            ),
            optimal_option="Flight B",
        ),
        TravelScenario(
            task=Task(
                goal="Choose the best business flight with baggage",
                context={
                    "traveler_type": "business",
                    "checked_baggage": True,
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 65000, 0),
                FlightOption("Flight B", 58000, 10000),
            ),
            optimal_option="Flight A",
        ),
        TravelScenario(
            task=Task(
                goal="Choose an international family flight",
                context={
                    "traveler_type": "family",
                    "checked_baggage": True,
                    "trip_type": "international",
                },
            ),
            options=(
                FlightOption("Flight A", 70000, 5000),
                FlightOption("Flight B", 65000, 10000),
            ),
            optimal_option="Flight A",
        ),
    ]


def create_test_scenarios() -> list[TravelScenario]:
    """Create unseen scenarios for the multi-experience benchmark."""

    return [
        # 1 — Exact E1 match.
        TravelScenario(
            task=Task(
                goal="Family domestic flight with baggage",
                context={
                    "traveler_type": "family",
                    "checked_baggage": True,
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 63000, 0),
                FlightOption("Flight B", 58000, 10000),
            ),
            optimal_option="Flight A",
        ),
        # 2 — Exact E2 match.
        TravelScenario(
            task=Task(
                goal="Family domestic flight without baggage",
                context={
                    "traveler_type": "family",
                    "checked_baggage": False,
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 63000, 5000),
                FlightOption("Flight B", 58000, 0),
            ),
            optimal_option="Flight B",
        ),
        # 3 — Exact E3 match.
        TravelScenario(
            task=Task(
                goal="Business domestic flight with baggage",
                context={
                    "traveler_type": "business",
                    "checked_baggage": True,
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 66000, 0),
                FlightOption("Flight B", 59000, 10000),
            ),
            optimal_option="Flight A",
        ),
        # 4 — Exact E4 match.
        TravelScenario(
            task=Task(
                goal="International family flight",
                context={
                    "traveler_type": "family",
                    "checked_baggage": True,
                    "trip_type": "international",
                },
            ),
            options=(
                FlightOption("Flight A", 71000, 5000),
                FlightOption("Flight B", 65000, 10000),
            ),
            optimal_option="Flight A",
        ),
        # 5 — Family + baggage, but international.
        # E1 and E4 may both be candidates.
        TravelScenario(
            task=Task(
                goal="International family flight with baggage",
                context={
                    "traveler_type": "family",
                    "checked_baggage": True,
                    "trip_type": "international",
                },
            ),
            options=(
                FlightOption("Flight A", 72000, 0),
                FlightOption("Flight B", 65000, 10000),
            ),
            optimal_option="Flight A",
        ),
        # 6 — Family + baggage with unknown trip type.
        # Applicability should become uncertain for experiences
        # requiring trip_type.
        TravelScenario(
            task=Task(
                goal="Family flight with baggage",
                context={
                    "traveler_type": "family",
                    "checked_baggage": True,
                },
            ),
            options=(
                FlightOption("Flight A", 73000, 0),
                FlightOption("Flight B", 66000, 10000),
            ),
            optimal_option="Flight A",
        ),
        # 7 — Business + baggage, international.
        TravelScenario(
            task=Task(
                goal="International business flight with baggage",
                context={
                    "traveler_type": "business",
                    "checked_baggage": True,
                    "trip_type": "international",
                },
            ),
            options=(
                FlightOption("Flight A", 74000, 0),
                FlightOption("Flight B", 66000, 10000),
            ),
            optimal_option="Flight A",
        ),
        # 8 — Family without baggage, international.
        TravelScenario(
            task=Task(
                goal="International family flight without baggage",
                context={
                    "traveler_type": "family",
                    "checked_baggage": False,
                    "trip_type": "international",
                },
            ),
            options=(
                FlightOption("Flight A", 70000, 5000),
                FlightOption("Flight B", 62000, 0),
            ),
            optimal_option="Flight B",
        ),
        # 9 — Business without baggage.
        TravelScenario(
            task=Task(
                goal="Business domestic flight without baggage",
                context={
                    "traveler_type": "business",
                    "checked_baggage": False,
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 65000, 5000),
                FlightOption("Flight B", 60000, 0),
            ),
            optimal_option="Flight B",
        ),
        # 10 — Family with missing baggage information.
        TravelScenario(
            task=Task(
                goal="Family domestic flight",
                context={
                    "traveler_type": "family",
                    "trip_type": "domestic",
                },
            ),
            options=(
                FlightOption("Flight A", 62000, 0),
                FlightOption("Flight B", 57000, 10000),
            ),
            optimal_option="Flight A",
        ),
    ]