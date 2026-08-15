from __future__ import annotations

from typing import Protocol
from uuid import UUID

from experience_os.models import Experience


class ExperienceStore(Protocol):
    """
    Abstract persistence interface.

    Any storage backend (SQLite, PostgreSQL,
    ChromaDB, MongoDB, etc.) should implement
    this interface.
    """

    def save(
        self,
        experience: Experience,
    ) -> None:
        """
        Persist an experience.
        """
        ...

    def load_all(
        self,
    ) -> list[Experience]:
        """
        Load every stored experience.
        """
        ...

    def delete(
        self,
        experience_id: UUID,
    ) -> None:
        """
        Delete an experience.
        """
        ...