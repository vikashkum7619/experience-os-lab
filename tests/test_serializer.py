from experience_os.models import Experience
from experience_os.serializer import ExperienceSerializer


def test_round_trip_serialization() -> None:
    experience = Experience(
        conditions={
            "country": "Japan",
        },
        decision_pattern=[
            "compare_total_cost",
        ],
        execution_count=5,
        successful_executions=4,
        confidence=0.8,
    )

    data = ExperienceSerializer.to_dict(
        experience,
    )

    restored = ExperienceSerializer.from_dict(
        data,
    )

    assert restored == experience