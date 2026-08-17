from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import UUID

from experience_os.episode import Episode


class EpisodeStore:
    """
    SQLite-backed storage for Episodes.

    Each episode is stored as a JSON document.
    """

    def __init__(
        self,
        database_path: str | Path = "episodes.db",
    ) -> None:

        self._connection = sqlite3.connect(str(database_path))
        self._connection.row_factory = sqlite3.Row

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS episodes (
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
        episode: Episode,
    ) -> None:
        """
        Insert or update an episode.
        """

        self._connection.execute(
            """
            INSERT OR REPLACE INTO episodes
            (id, data)
            VALUES (?, ?)
            """,
            (
                str(episode.id),
                json.dumps(
                    episode.model_dump(
                        mode="json",
                    )
                ),
            ),
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    def all(
        self,
    ) -> list[Episode]:
        """
        Return all stored episodes.
        """

        cursor = self._connection.execute(
            """
            SELECT data
            FROM episodes
            """
        )

        episodes: list[Episode] = []

        for row in cursor.fetchall():
            payload = json.loads(
                row["data"]
            )

            episodes.append(
                Episode.model_validate(
                    payload,
                )
            )

        return episodes

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete(
        self,
        episode_id: UUID,
    ) -> None:
        """
        Delete an episode.
        """

        self._connection.execute(
            """
            DELETE FROM episodes
            WHERE id = ?
            """,
            (
                str(episode_id),
            ),
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove every stored episode.
        """

        self._connection.execute(
            "DELETE FROM episodes"
        )

        self._connection.commit()

    # ---------------------------------------------------------
    # Stats
    # ---------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Return the number of stored episodes.
        """

        cursor = self._connection.execute(
            """
            SELECT COUNT(*)
            FROM episodes
            """
        )

        return int(cursor.fetchone()[0])

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def close(
        self,
    ) -> None:
        self._connection.close()

    def __enter__(
        self,
    ) -> "EpisodeStore":
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self.close()