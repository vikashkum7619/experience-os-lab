from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import UUID

from experience_os.models import Experience
from experience_os.persistence import ExperienceStore
from experience_os.serializer import ExperienceSerializer


class SQLiteExperienceStore(ExperienceStore):
    """
    SQLite-backed implementation of ExperienceStore.
    """

    def __init__(
        self,
        database_path: str | Path = "experience.db",
    ) -> None:

        self._connection = sqlite3.connect(str(database_path))
        self._connection.row_factory = sqlite3.Row

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

        payload = ExperienceSerializer.to_dict(
            experience
        )

        self._connection.execute(
            """
            INSERT OR REPLACE INTO experiences
            (id, data)
            VALUES (?, ?)
            """,
            (
                str(experience.id),
                json.dumps(payload),
            ),
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Compatibility API
    # ---------------------------------------------------------

    def add(
        self,
        experience: Experience,
    ) -> None:
        """
        Compatibility with the in-memory ExperienceStore.
        """
        self.save(experience)

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    def load_all(
        self,
    ) -> list[Experience]:

        cursor = self._connection.execute(
            """
            SELECT data
            FROM experiences
            """
        )

        experiences: list[Experience] = []

        for row in cursor.fetchall():
            payload = json.loads(row["data"])

            experiences.append(
                ExperienceSerializer.from_dict(payload)
            )

        return experiences

    def all(self) -> list[Experience]:
        return self.load_all()

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete(
        self,
        experience_id: UUID,
    ) -> None:

        self._connection.execute(
            """
            DELETE FROM experiences
            WHERE id = ?
            """,
            (str(experience_id),),
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:

        self._connection.execute(
            "DELETE FROM experiences"
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def close(self) -> None:
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        self.close()