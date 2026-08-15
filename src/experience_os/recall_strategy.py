from __future__ import annotations

from abc import ABC, abstractmethod

from experience_os.models import Experience, Task
from experience_os.recall import ExperienceRecall


class RecallStrategy(ABC):
    """
    Abstract interface for retrieving relevant experiences.

    Different retrieval implementations (exact matching,
    semantic search, hybrid search, etc.) should implement
    this interface.
    """

    @abstractmethod
    def recall(
        self,
        task: Task,
    ) -> list[Experience]:
        """
        Retrieve experiences relevant to the supplied task.
        """
        raise NotImplementedError


class ExactRecallStrategy(RecallStrategy):
    """
    Uses the existing deterministic ExperienceRecall engine.
    """

    def __init__(
        self,
        recall_engine: ExperienceRecall,
    ) -> None:
        self._recall_engine = recall_engine

    def recall(
        self,
        task: Task,
    ) -> list[Experience]:
        return self._recall_engine.recall(task)


class SemanticRecallStrategy(RecallStrategy):
    """
    Placeholder for embedding/vector retrieval.

    This will be implemented later using an embedding model
    and a vector database.
    """

    def recall(
        self,
        task: Task,
    ) -> list[Experience]:
        raise NotImplementedError(
            "Semantic recall has not been implemented yet."
        )


class HybridRecallStrategy(RecallStrategy):
    """
    Placeholder for hybrid retrieval.

    Future implementation:

    - Exact matching
    - Vector similarity
    - Metadata filters
    - Ranking
    """

    def recall(
        self,
        task: Task,
    ) -> list[Experience]:
        raise NotImplementedError(
            "Hybrid recall has not been implemented yet."
        )