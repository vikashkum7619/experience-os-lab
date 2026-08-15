from experience_os.models import Experience
from experience_os.sqlite_store import SQLiteExperienceStore


def build_experience() -> Experience:
    return Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=[
            "compare_total_cost",
        ],
        execution_count=1,
        successful_executions=1,
        confidence=1.0,
    )


def test_empty_store(tmp_path) -> None:
    store = SQLiteExperienceStore(
        tmp_path / "experience.db"
    )

    assert store.load_all() == []

    store.close()


def test_save_and_load(tmp_path) -> None:
    store = SQLiteExperienceStore(
        tmp_path / "experience.db"
    )

    experience = build_experience()

    store.save(experience)

    loaded = store.load_all()

    assert len(loaded) == 1
    assert loaded[0] == experience

    store.close()


def test_delete(tmp_path) -> None:
    store = SQLiteExperienceStore(
        tmp_path / "experience.db"
    )

    experience = build_experience()

    store.save(experience)

    store.delete(
        experience.id,
    )

    assert store.load_all() == []

    store.close()


def test_persistence_across_restart(tmp_path) -> None:
    database = tmp_path / "experience.db"

    experience = build_experience()

    store = SQLiteExperienceStore(database)

    store.save(experience)

    store.close()

    reopened = SQLiteExperienceStore(database)

    loaded = reopened.load_all()

    assert len(loaded) == 1
    assert loaded[0] == experience

    reopened.close()