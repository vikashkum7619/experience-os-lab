from experience_os.embeddings import DummyEmbeddingProvider
from experience_os.models import Experience
from experience_os.semantic_index import SemanticIndex


def build_experience(text: str) -> Experience:
    return Experience(
        decision_pattern=[text],
    )


def test_index_adds_experience() -> None:
    index = SemanticIndex(
        DummyEmbeddingProvider(),
    )

    index.add(build_experience("family travel"))

    assert index.size == 1


def test_search_returns_results() -> None:
    index = SemanticIndex(
        DummyEmbeddingProvider(),
    )

    first = build_experience("family vacation")
    second = build_experience("business travel")

    index.add(first)
    index.add(second)

    results = index.search("family trip")

    assert len(results) == 2


def test_top_k_limits_results() -> None:
    index = SemanticIndex(
        DummyEmbeddingProvider(),
    )

    for i in range(10):
        index.add(
            build_experience(f"experience {i}")
        )

    results = index.search(
        "experience",
        top_k=3,
    )

    assert len(results) == 3


def test_empty_index_returns_empty_list() -> None:
    index = SemanticIndex(
        DummyEmbeddingProvider(),
    )

    assert index.search("anything") == []