from experience_os.persistence import ExperienceStore


def test_protocol_exists() -> None:
    """
    Smoke test.

    Confirms the protocol can be imported.
    """
    assert ExperienceStore is not None