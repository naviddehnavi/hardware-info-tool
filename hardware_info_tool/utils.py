"""Shared formatting helpers."""

from __future__ import annotations


def bytes_to_gib(value: int | float | None) -> str:
    """Return a human-readable GiB value."""
    if value is None:
        return "Unknown"
    return f"{value / (1024 ** 3):.2f} GiB"


def percent(value: int | float | None) -> str:
    """Return a percentage value or Unknown."""
    if value is None:
        return "Unknown"
    return f"{value}%"
