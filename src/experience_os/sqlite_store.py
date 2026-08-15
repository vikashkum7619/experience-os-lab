from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import UUID

from experience_os.models import Experience
from experience_os.persistence import ExperienceStore
from experience_os.serializer import ExperienceSerializer


class SQLiteExperienceStore(ExperienceStore):
    """
    SQLite-backed implementation of ExperienceStore.

    Experiences are stored as serialized JSON, allowing the
    Experience model to evolve without frequent schema changes.
    """

    def __init__(
        self,
        database_path: str | Path = "experience.db",
    ) -> None:
        self._database_path = Path(database_path)

        self._connection = sqlite3.connect(
            self._database_path
        )

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS experiences (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
            """
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def save(
        self,
        experience: Experience,
    ) -> None:
        """
        Insert or update an experience.
        """

        payload = ExperienceSerializer.to_dict(
            experience,
        )

        self._connection.execute(
            """
            INSERT OR REPLACE INTO experiences
            (id, data)
            VALUES (?, ?)
            """,
            (
                str(experience.id),
                experience.model_dump_json(),
            ),
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    def load_all(
        self,
    ) -> list[Experience]:
        """
        Load every stored experience.
        """

        cursor = self._connection.execute(
            """
            SELECT data
            FROM experiences
            """
        )

        experiences: list[Experience] = []

        for (json_data,) in cursor.fetchall():
            experiences.append(
                Experience.model_validate_json(
                    json_data,
                )
            )

        return experiences

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete(
        self,
        experience_id: UUID,
    ) -> None:
        """
        Delete an experience.
        """

        self._connection.execute(
            """
            DELETE FROM experiences
            WHERE id = ?
            """,
            (
                str(experience_id),
            ),
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def close(
        self,
    ) -> None:
        """
        Close the SQLite connection.
        """

        self._connection.close()

    def __enter__(
        self,
    ) -> "SQLiteExperienceStore":
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.close()