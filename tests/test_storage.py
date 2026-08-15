from __future__ import annotations

from pathlib import Path

from experience_os.models import Experience
from experience_os.storage import ExperienceStorage


def make_experience(
    traveler_type: str = "family",
) -> Experience:
    return Experience(
        conditions={
            "traveler_type": traveler_type,
        },
        decision_pattern=[
            f"{traveler_type} strategy",
        ],
        execution_count=10,
        successful_executions=9,
        confidence=0.9,
    )


def test_storage_initially_empty(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    assert storage.exists() is False
    assert storage.load() == []
    assert storage.count() == 0


def test_storage_exists_after_save(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    storage.save(
        [
            make_experience(),
        ]
    )

    assert storage.exists()


def test_save_and_load_single_experience(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    experience = make_experience()

    storage.save(
        [experience]
    )

    loaded = storage.load()

    assert len(loaded) == 1
    assert loaded[0].id == experience.id
    assert (
        loaded[0].decision_pattern
        == experience.decision_pattern
    )
    assert (
        loaded[0].conditions
        == experience.conditions
    )


def test_save_and_load_multiple_experiences(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    experiences = [
        make_experience("family"),
        make_experience("business"),
        make_experience("solo"),
    ]

    storage.save(experiences)

    loaded = storage.load()

    assert len(loaded) == 3

    traveler_types = {
        exp.conditions["traveler_type"]
        for exp in loaded
    }

    assert traveler_types == {
        "family",
        "business",
        "solo",
    }


def test_delete_storage(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    storage.save(
        [
            make_experience(),
        ]
    )

    assert storage.exists()

    storage.delete()

    assert not storage.exists()


def test_clear_storage(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    storage.save(
        [
            make_experience(),
        ]
    )

    storage.clear()

    assert storage.exists() is False


def test_count_returns_number_of_experiences(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    storage.save(
        [
            make_experience("family"),
            make_experience("business"),
            make_experience("solo"),
        ]
    )

    assert storage.count() == 3


def test_loading_missing_file_returns_empty_list(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "missing.json",
    )

    assert storage.load() == []


def test_save_overwrites_previous_contents(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    storage.save(
        [
            make_experience("family"),
        ]
    )

    storage.save(
        [
            make_experience("business"),
        ]
    )

    loaded = storage.load()

    assert len(loaded) == 1
    assert (
        loaded[0].conditions["traveler_type"]
        == "business"
    )


def test_loaded_experience_preserves_confidence(
    tmp_path: Path,
) -> None:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    experience = make_experience()

    storage.save(
        [
            experience,
        ]
    )

    loaded = storage.load()

    assert (
        loaded[0].confidence
        == experience.confidence
    )