"""Units as data, grouped by quantity."""

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


def _keys(unit: Unit) -> tuple[str, ...]:
    return tuple(spelling.casefold() for spelling in (unit.symbol, unit.name, *unit.aliases))


class Registry:
    """Quantities by name, with case-insensitive unit lookup."""

    def __init__(self) -> None:
        self._quantities: list[Quantity] = []
        self._units: dict[str, tuple[Quantity, Unit]] = {}

    def register(self, quantity: Quantity) -> None:
        """Add a quantity and its units.

        Raises ``ValueError``, leaving the registry unchanged, if any symbol, name or alias
        matches one already registered (case-insensitive).
        """
        new_units: dict[str, tuple[Quantity, Unit]] = {}
        for unit in quantity.units:
            for key in set(_keys(unit)):
                if key in self._units or key in new_units:
                    raise ValueError(f"unit spelling already registered: {key!r}")
                new_units[key] = (quantity, unit)
        self._quantities.append(quantity)
        self._units.update(new_units)

    def quantities(self) -> tuple[Quantity, ...]:
        """The registered quantities, in registration order."""
        return tuple(self._quantities)

    def find(self, spelling: str) -> tuple[Quantity, Unit] | None:
        """The quantity and unit for a symbol, name or alias in any case; ``None`` if unknown."""
        return self._units.get(spelling.casefold())


def build_default_registry() -> Registry:
    """A fresh registry holding the built-in quantities."""
    registry = Registry()
    registry.register(
        Quantity(
            name="temperature",
            base="K",
            units=(
                Unit(symbol="C", name="celsius", factor=1.0, offset=273.15),
                Unit(symbol="F", name="fahrenheit", factor=5 / 9, offset=459.67 * 5 / 9),
                Unit(symbol="K", name="kelvin", factor=1.0, offset=0.0),
            ),
            min_base=0.0,
        )
    )
    return registry


DEFAULT_REGISTRY = build_default_registry()
