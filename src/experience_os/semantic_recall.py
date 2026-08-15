from __future__ import annotations

from experience_os.models import Experience, Task
from experience_os.recall import ExperienceRecall
from experience_os.semantic_index import SemanticIndex


class SemanticRecall:
    """
    Hybrid recall strategy.

    Combines:

    1. Symbolic recall (exact condition matching)
    2. Semantic recall (vector similarity)

    Duplicate experiences are automatically removed while
    preserving ranking order.
    """

    def __init__(
        self,
        symbolic_recall: ExperienceRecall,
        semantic_index: SemanticIndex,
    ) -> None:
        self._symbolic_recall = symbolic_recall
        self._semantic_index = semantic_index

    def recall(
        self,
        task: Task,
        *,
        top_k: int = 5,
    ) -> list[Experience]:
        """
        Recall experiences using both symbolic and semantic search.
        """

        symbolic = self._symbolic_recall.recall(task)

        query = self._build_query(task)

        semantic = self._semantic_index.search(
            query,
            top_k=top_k,
        )

        return self._merge(
            symbolic,
            semantic,
        )

    @staticmethod
    def _build_query(
        task: Task,
    ) -> str:
        """
        Convert a task into a searchable text representation.
        """

        parts: list[str] = [task.goal]

        for key, value in task.context.items():
            parts.append(f"{key}: {value}")

        for key, value in task.constraints.items():
            parts.append(f"{key}: {value}")

        return " ".join(parts)

    @staticmethod
    def _merge(
        symbolic: list[Experience],
        semantic: list[Experience],
    ) -> list[Experience]:
        """
        Merge recall results while removing duplicates.

        Symbolic matches always appear first because they are
        exact matches.
        """

        merged: list[Experience] = []
        seen: set[str] = set()

        for experience in symbolic + semantic:
            key = str(experience.id)

            if key in seen:
                continue

            seen.add(key)
            merged.append(experience)

        return merged
