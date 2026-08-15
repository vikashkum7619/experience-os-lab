from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from experience_os.embeddings import EmbeddingProvider
from experience_os.models import Experience


@dataclass(slots=True)
class IndexedExperience:
    """
    Experience together with its embedding vector.
    """

    experience: Experience
    vector: list[float]


class SemanticIndex:
    """
    Simple in-memory semantic index.

    Stores embedding vectors and performs cosine similarity search.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
    ) -> None:

        self._embedding_provider = embedding_provider
        self._items: list[IndexedExperience] = []

    @property
    def size(self) -> int:
        return len(self._items)

    def add(
        self,
        experience: Experience,
    ) -> None:

        text = " ".join(experience.decision_pattern)

        vector = self._embedding_provider.embed(text)

        self._items.append(
            IndexedExperience(
                experience=experience,
                vector=vector,
            )
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Experience]:

        query_vector = self._embedding_provider.embed(query)

        ranked = sorted(
            self._items,
            key=lambda item: self._cosine(
                query_vector,
                item.vector,
            ),
            reverse=True,
        )

        return [
            item.experience
            for item in ranked[:top_k]
        ]

    @staticmethod
    def _cosine(
        a: list[float],
        b: list[float],
    ) -> float:

        dot = sum(x * y for x, y in zip(a, b))

        norm_a = sqrt(sum(x * x for x in a))
        norm_b = sqrt(sum(y * y for y in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)