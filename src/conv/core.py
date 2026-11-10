"""Conversion between units of a registry.

Stub: ``convert`` is built by the library feature.
"""

from conv.registry import Registry


class ConversionError(ValueError):
    """A value or unit that cannot be converted."""


def convert(value: float, from_unit: str, to_unit: str, registry: Registry | None = None) -> float:
    """Convert ``value`` from ``from_unit`` to ``to_unit``."""
    return float("nan")
