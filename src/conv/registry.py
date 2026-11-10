"""Units as data, grouped by quantity.

Stub: the data types are in place; registration, lookup and the default
temperature registry are built by the library feature.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
    """A unit, affine to its quantity's base unit: ``base = value * factor + offset``."""

    symbol: str
    name: str
    aliases: tuple[str, ...] = ()
    factor: float = 1.0
    offset: float = 0.0


@dataclass(frozen=True)
class Quantity:
    """A quantity: its base unit symbol, its units in order, an optional minimum base value."""

    name: str
    base: str
    units: tuple[Unit, ...]
    min_base: float | None = None


class Registry:
    """Quantities by name, with case-insensitive unit lookup."""

    def register(self, quantity: Quantity) -> None:
        """Add a quantity and its units."""

    def quantities(self) -> tuple[Quantity, ...]:
        """The registered quantities, in registration order."""
        return ()


def build_default_registry() -> Registry:
    """A fresh registry holding the built-in quantities."""
    return Registry()


DEFAULT_REGISTRY = build_default_registry()
