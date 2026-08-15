from __future__ import annotations

import json
from pathlib import Path

from experience_os.models import Experience


class ExperienceStorage:
    """
    Persistent storage for Experience OS.

    Gen-1 stores all experiences in a single JSON file.
    """

    def __init__(
        self,
        path: Path,
    ) -> None:
        self._path = path

    def exists(self) -> bool:
        """
        Return True if the storage file exists.
        """
        return self._path.exists()

    def save(
        self,
        experiences: list[Experience],
    ) -> None:
        """
        Save all experiences to disk.
        """

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = [
            self._serialize(exp)
            for exp in experiences
        ]

        self._path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def load(
        self,
    ) -> list[Experience]:
        """
        Load all experiences from disk.
        """

        if not self.exists():
            return []

        payload = json.loads(
            self._path.read_text(
                encoding="utf-8",
            )
        )

        return [
            self._deserialize(item)
            for item in payload
        ]

    def count(self) -> int:
        """
        Return the number of stored experiences.
        """

        return len(self.load())

    def clear(self) -> None:
        """
        Remove the storage file.
        """

        if self.exists():
            self._path.unlink()

    def delete(self) -> None:
        """
        Delete the storage file.

        Alias for clear().
        """

        self.clear()

    def _serialize(
        self,
        experience: Experience,
    ) -> dict:
        """
        Convert an Experience into a JSON-compatible dictionary.
        """

        return experience.model_dump(
            mode="json",
        )

    def _deserialize(
        self,
        data: dict,
    ) -> Experience:
        """
        Convert a dictionary back into an Experience.
        """

        return Experience.model_validate(data)