from experience_os.models import Experience, Task
from experience_os.ranking import ExperienceRanker


def test_perfect_similarity_scores_one() -> None:
    ranker = ExperienceRanker()

    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["check_baggage"],
        confidence=0.80,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
            "checked_baggage": True,
        },
    )

    score = ranker.score(experience, task)

    assert score.similarity == 1.0


def test_partial_similarity() -> None:
    ranker = ExperienceRanker()

    experience = Experience(
        conditions={
            "traveler_type": "family",
            "checked_baggage": True,
        },
        decision_pattern=["check_baggage"],
        confidence=0.80,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
            "checked_baggage": False,
        },
    )

    score = ranker.score(experience, task)

    assert score.similarity == 0.5


def test_no_similarity() -> None:
    ranker = ExperienceRanker()

    experience = Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=["check_baggage"],
        confidence=0.80,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "business",
        },
    )

    score = ranker.score(experience, task)

    assert score.similarity == 0.0


def test_total_score_uses_similarity_and_trust() -> None:
    ranker = ExperienceRanker()

    experience = Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=["check_baggage"],
        confidence=0.50,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
        },
    )

    score = ranker.score(experience, task)

    expected = (1.0 * 0.6) + (0.5 * 0.4)

    assert score.total_score == expected


def test_rank_returns_highest_score_first() -> None:
    ranker = ExperienceRanker()

    best = Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=["best"],
        confidence=1.0,
    )

    worst = Experience(
        conditions={
            "traveler_type": "business",
        },
        decision_pattern=["worst"],
        confidence=0.20,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
        },
    )

    ranked = ranker.rank(
        [worst, best],
        task,
    )

    assert ranked[0].experience == best
    assert ranked[1].experience == worst


def test_rank_empty_list() -> None:
    ranker = ExperienceRanker()

    task = Task(goal="Book flight")

    ranked = ranker.rank([], task)

    assert ranked == []


def test_trust_breaks_tie() -> None:
    ranker = ExperienceRanker()

    high_trust = Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=["high"],
        confidence=0.90,
    )

    low_trust = Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=["low"],
        confidence=0.30,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
        },
    )

    ranked = ranker.rank(
        [low_trust, high_trust],
        task,
    )

    assert ranked[0].experience == high_trust


def test_empty_conditions_have_zero_similarity() -> None:
    ranker = ExperienceRanker()

    experience = Experience(
        conditions={},
        decision_pattern=["general"],
        confidence=1.0,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
        },
    )

    score = ranker.score(experience, task)

    assert score.similarity == 0.0


def test_score_is_between_zero_and_one() -> None:
    ranker = ExperienceRanker()

    experience = Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=["general"],
        confidence=0.75,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
        },
    )

    score = ranker.score(experience, task)

    assert 0.0 <= score.total_score <= 1.0


def test_rank_is_deterministic() -> None:
    ranker = ExperienceRanker()

    experience = Experience(
        conditions={
            "traveler_type": "family",
        },
        decision_pattern=["general"],
        confidence=0.80,
    )

    task = Task(
        goal="Book flight",
        context={
            "traveler_type": "family",
        },
    )

    first = ranker.rank([experience], task)
    second = ranker.rank([experience], task)

    assert first[0].total_score == second[0].total_score