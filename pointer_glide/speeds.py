"""Speeds for the ten glide modes."""

from __future__ import annotations

MODES = range(1, 11)
BASE_SPEED = 600.0


def speed_for(mode: int, base: float = BASE_SPEED) -> float:
    """Pixels per second for *mode*: 1 is the fastest, 10 the slowest."""
    if mode not in MODES:
        raise ValueError(f"mode must be between 1 and 10, got {mode!r}")
    return base / mode


def describe(base: float = BASE_SPEED) -> list[tuple[int, float]]:
    return [(mode, speed_for(mode, base)) for mode in MODES]
