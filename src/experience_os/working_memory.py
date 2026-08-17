from __future__ import annotations

from collections import deque
from typing import Iterable

from experience_os.episode import Episode
from experience_os.models import Experience


class WorkingMemory:
    """
    Short-term memory used during a single execution.

    Working memory is intentionally ephemeral. It keeps only the
    information needed while solving the current task.

    It stores:

    - Recent episodes
    - Relevant experiences
    - Current reasoning notes
    """

    def __init__(
        self,
        *,
        max_episodes: int = 20,
        max_experiences: int = 20,
    ) -> None:

        self._episodes: deque[Episode] = deque(
            maxlen=max_episodes,
        )

        self._experiences: deque[Experience] = deque(
            maxlen=max_experiences,
        )

        self._notes: list[str] = []

    # ---------------------------------------------------------
    # Episodes
    # ---------------------------------------------------------

    def add_episode(
        self,
        episode: Episode,
    ) -> None:
        """
        Add a recently executed episode.
        """
        self._episodes.append(episode)

    def episodes(
        self,
    ) -> list[Episode]:
        """
        Return all episodes in working memory.
        """
        return list(self._episodes)

    # ---------------------------------------------------------
    # Experiences
    # ---------------------------------------------------------

    def add_experience(
        self,
        experience: Experience,
    ) -> None:
        """
        Add a recalled experience.
        """
        self._experiences.append(experience)

    def add_experiences(
        self,
        experiences: Iterable[Experience],
    ) -> None:
        """
        Add multiple recalled experiences.
        """
        self._experiences.extend(experiences)

    def experiences(
        self,
    ) -> list[Experience]:
        """
        Return all recalled experiences.
        """
        return list(self._experiences)

    # ---------------------------------------------------------
    # Notes
    # ---------------------------------------------------------

    def add_note(
        self,
        note: str,
    ) -> None:
        """
        Add a reasoning note.
        """
        if note:
            self._notes.append(note)

    def notes(
        self,
    ) -> list[str]:
        """
        Return reasoning notes.
        """
        return list(self._notes)

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def latest_episode(
        self,
    ) -> Episode | None:
        """
        Return the most recent episode.
        """
        if not self._episodes:
            return None

        return self._episodes[-1]

    def latest_experience(
        self,
    ) -> Experience | None:
        """
        Return the most recent recalled experience.
        """
        if not self._experiences:
            return None

        return self._experiences[-1]

    @property
    def episode_count(
        self,
    ) -> int:
        return len(self._episodes)

    @property
    def experience_count(
        self,
    ) -> int:
        return len(self._experiences)

    @property
    def note_count(
        self,
    ) -> int:
        return len(self._notes)

    def empty(
        self,
    ) -> bool:
        """
        Return True if working memory contains no information.
        """
        return (
            not self._episodes
            and not self._experiences
            and not self._notes
        )

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Reset working memory.
        """
        self._episodes.clear()
        self._experiences.clear()
        self._notes.clear()