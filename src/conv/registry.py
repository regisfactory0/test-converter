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
    """A quantity: its base unit symbol, its units in order, an optional minimum base value.

    Base values below ``min_base`` by at most ``min_tolerance`` are clamped to it; ``None``
    means the core's default tolerance. ``below_min_message`` replaces the generic error text.
    """

    name: str
    base: str
    units: tuple[Unit, ...]
    min_base: float | None = None
    min_tolerance: float | None = None
    below_min_message: str | None = None


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
            below_min_message="value is below absolute zero",
        )
    )
    return registry


def build_distance_registry() -> Registry:
    """A fresh registry holding only distance, in metric and international imperial units."""
    registry = Registry()
    registry.register(
        Quantity(
            name="distance",
            base="m",
            units=(
                Unit(symbol="mm", name="millimetre", aliases=("millimeter",), factor=0.001),
                Unit(symbol="cm", name="centimetre", aliases=("centimeter",), factor=0.01),
                Unit(symbol="m", name="metre", aliases=("meter",), factor=1.0),
                Unit(symbol="km", name="kilometre", aliases=("kilometer",), factor=1000.0),
                Unit(symbol="in", name="inch", factor=0.0254),
                Unit(symbol="ft", name="foot", factor=0.3048),
                Unit(symbol="yd", name="yard", factor=0.9144),
                Unit(symbol="mi", name="mile", factor=1609.344),
            ),
            min_base=0.0,
            min_tolerance=0.0,
            below_min_message="value is negative",
        )
    )
    return registry


DEFAULT_REGISTRY = build_default_registry()
DISTANCE_REGISTRY = build_distance_registry()
