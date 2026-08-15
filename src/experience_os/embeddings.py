from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Abstract embedding interface.

    Different embedding models (OpenAI, BGE, MiniLM,
    VoyageAI, etc.) should all implement this interface.
    """

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """
        Convert text into a dense vector.
        """
        raise NotImplementedError


class DummyEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic embedding provider used for tests.

    This is NOT intended for production.
    """

    VECTOR_SIZE = 8

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.VECTOR_SIZE

        for index, character in enumerate(text.lower()):
            vector[index % self.VECTOR_SIZE] += ord(character)

        norm = sum(v * v for v in vector) ** 0.5

        if norm == 0:
            return vector

        return [v / norm for v in vector]