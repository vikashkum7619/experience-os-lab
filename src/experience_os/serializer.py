from __future__ import annotations

from experience_os.models import Experience


class ExperienceSerializer:
    """
    Serialize and deserialize Experience objects.
    """

    @staticmethod
    def to_dict(
        experience: Experience,
    ) -> dict:
        """
        Convert an Experience into a dictionary.
        """
        return experience.model_dump(mode="json")

    @staticmethod
    def from_dict(
        data: dict,
    ) -> Experience:
        """
        Create an Experience from a dictionary.
        """
        return Experience.model_validate(data)