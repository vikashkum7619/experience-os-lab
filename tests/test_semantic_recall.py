from experience_os.embeddings import DummyEmbeddingProvider
from experience_os.models import Experience, Task
from experience_os.semantic_index import SemanticIndex
from experience_os.semantic_recall import SemanticRecall


class DummyRecall:
    """
    Minimal symbolic recall implementation for tests.
    """

    def __init__(self, experiences):
        self._experiences = experiences

    def recall(self, task):
        del task
        return self._experiences


def build_experience(text: str) -> Experience:
    return Experience(
        decision_pattern=[text],
    )


def test_semantic_recall_combines_results() -> None:
    first = build_experience("family vacation")
    second = build_experience("business travel")

    index = SemanticIndex(
        DummyEmbeddingProvider(),
    )

    index.add(first)
    index.add(second)

    recall = SemanticRecall(
        DummyRecall([first]),
        index,
    )

    task = Task(goal="family trip")

    results = recall.recall(task)

    assert len(results) >= 2


def test_duplicates_removed() -> None:
    experience = build_experience("family vacation")

    index = SemanticIndex(
        DummyEmbeddingProvider(),
    )

    index.add(experience)

    recall = SemanticRecall(
        DummyRecall([experience]),
        index,
    )

    task = Task(goal="family trip")

    results = recall.recall(task)

    assert len(results) == 1


def test_query_contains_goal() -> None:
    task = Task(
        goal="book flight",
        context={"traveler_type": "family"},
        constraints={"budget": 50000},
    )

    query = SemanticRecall._build_query(task)

    assert "book flight" in query
    assert "traveler_type" in query
    assert "budget" in query