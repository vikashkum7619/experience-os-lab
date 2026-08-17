from __future__ import annotations

from dataclasses import dataclass

from experience_os.models import Experience, Task
from experience_os.episode import Episode
from experience_os.working_memory import WorkingMemory
from experience_os.semantic_recall import SemanticRecall


@dataclass(slots=True)
class Context:
    """
    Context assembled for planning or LLM reasoning.
    """

    task: Task
    experiences: list[Experience]
    recent_episodes: list[Episode]
    notes: list[str]


class ContextBuilder:
    """
    Builds execution context by combining:

    - Current task
    - Working memory
    - Relevant experiences
    """

    def __init__(
        self,
        recall: SemanticRecall,
        working_memory: WorkingMemory,
    ) -> None:
        self._recall = recall
        self._working_memory = working_memory

    def build(
        self,
        task: Task,
        *,
        top_k: int = 5,
    ) -> Context:
        """
        Build a context for planning or LLM inference.
        """

        experiences = self._recall.recall(
            task,
            top_k=top_k,
        )

        return Context(
            task=task,
            experiences=experiences,
            recent_episodes=self._working_memory.episodes(),
            notes=self._working_memory.notes(),
        )

    def refresh(
        self,
        task: Task,
        *,
        top_k: int = 5,
    ) -> Context:
        """
        Refresh the context after working memory changes.
        """

        return self.build(
            task,
            top_k=top_k,
        )