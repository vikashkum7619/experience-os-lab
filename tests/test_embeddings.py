from experience_os.embeddings import DummyEmbeddingProvider


def test_embeddings_are_deterministic() -> None:
    provider = DummyEmbeddingProvider()

    first = provider.embed("family vacation")
    second = provider.embed("family vacation")

    assert first == second


def test_embedding_dimension() -> None:
    provider = DummyEmbeddingProvider()

    vector = provider.embed("hello")

    assert len(vector) == provider.VECTOR_SIZE


def test_different_texts_produce_different_vectors() -> None:
    provider = DummyEmbeddingProvider()

    first = provider.embed("family")

    second = provider.embed("business")

    assert first != second