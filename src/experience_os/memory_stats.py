from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MemoryStats:
    """
    High-level statistics about the memory.
    """

    total_experiences: int
    average_confidence: float
    average_success_rate: float