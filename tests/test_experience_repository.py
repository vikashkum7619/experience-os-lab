from __future__ import annotations

from pathlib import Path

from experience_os.experience_repository import ExperienceRepository
from experience_os.lifecycle import ExperienceState
from experience_os.models import Experience
from experience_os.storage import ExperienceStorage


def make_repository(
    tmp_path: Path,
) -> ExperienceRepository:
    storage = ExperienceStorage(
        tmp_path / "experiences.json",
    )

    return ExperienceRepository(storage)


def make_experience(
    traveler_type: str = "family",
) -> Experience:
    return Experience(
        conditions={
            "traveler_type": traveler_type,
        },
        decision_pattern=[
            "Book direct flight",
        ],
        execution_count=10,
        successful_executions=8,
        confidence=0.75,
    )


def test_repository_is_initially_empty(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    assert repository.count() == 0


def test_add_experience(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    experience = make_experience()

    repository.add(experience)

    assert repository.count() == 1


def test_get_experience(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    experience = make_experience()

    repository.add(experience)

    loaded = repository.get(
        experience.id,
    )

    assert loaded is not None
    assert loaded.id == experience.id


def test_exists_returns_true(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    experience = make_experience()

    repository.add(experience)

    assert repository.exists(
        experience.id,
    )


def test_exists_returns_false(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    assert not repository.exists(
        make_experience().id,
    )


def test_remove_experience(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    experience = make_experience()

    repository.add(experience)

    assert repository.remove(
        experience.id,
    )

    assert repository.count() == 0


def test_remove_unknown_returns_false(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    assert not repository.remove(
        make_experience().id,
    )


def test_update_experience(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    experience = make_experience()

    repository.add(experience)

    experience.confidence = 0.95

    repository.update(experience)

    loaded = repository.get(
        experience.id,
    )

    assert loaded is not None
    assert loaded.confidence == 0.95


def test_all_returns_everything(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    repository.add(
        make_experience("family"),
    )

    repository.add(
        make_experience("business"),
    )

    assert len(repository.all()) == 2


def test_clear_repository(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    repository.add(
        make_experience(),
    )

    repository.clear()

    assert repository.count() == 0


def test_save_repository(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    repository.add(
        make_experience(),
    )

    repository.save()

    assert repository.storage.exists()


def test_load_repository(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    repository.add(
        make_experience(),
    )

    repository.save()

    loaded = make_repository(tmp_path)

    loaded.load()

    assert loaded.count() == 1


def test_state_returns_lifecycle_state(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    experience = make_experience()

    state = repository.state(
        experience,
    )

    assert state == ExperienceState.VALIDATED


def test_archive_returns_archived(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    state = repository.archive(
        make_experience(),
    )

    assert state == ExperienceState.ARCHIVED


def test_promote_returns_state(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    state = repository.promote(
        make_experience(),
    )

    assert state == ExperienceState.VALIDATED


def test_demote_returns_state(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    state = repository.demote(
        make_experience(),
    )

    assert state == ExperienceState.VALIDATED


def test_refresh_returns_state(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    state = repository.refresh(
        make_experience(),
    )

    assert state == ExperienceState.VALIDATED


def test_repository_storage_property(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    assert repository.storage is not None


def test_repository_memory_property(
    tmp_path: Path,
) -> None:
    repository = make_repository(tmp_path)

    assert repository.memory is not None