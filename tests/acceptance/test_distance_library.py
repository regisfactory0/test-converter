"""Acceptance tests: the distance registry and library conversion."""

import itertools
import math
from typing import Any

import pytest

from conv import ConversionError, convert

pytestmark = pytest.mark.feature("distance-library")

SYMBOLS = ("mm", "cm", "m", "km", "in", "ft", "yd", "mi")


def distance_registry() -> Any:
    """A fresh distance registry (imported here: the function is new in this feature)."""
    from conv.registry import build_distance_registry

    return build_distance_registry()


def test_distance_registry_contents() -> None:
    """AC-6.1: the distance registry holds exactly `distance`, base `m`, units in order."""
    registry = distance_registry()
    quantities = registry.quantities()
    assert [quantity.name for quantity in quantities] == ["distance"]
    distance = quantities[0]
    assert distance.base == "m"
    assert [(unit.symbol, unit.name) for unit in distance.units] == [
        ("mm", "millimetre"),
        ("cm", "centimetre"),
        ("m", "metre"),
        ("km", "kilometre"),
        ("in", "inch"),
        ("ft", "foot"),
        ("yd", "yard"),
        ("mi", "mile"),
    ]


def test_distance_registry_is_fresh() -> None:
    """AC-6.1: each call returns a new registry instance."""
    assert distance_registry() is not distance_registry()


@pytest.mark.parametrize(
    ("src", "dst", "expected"),
    [
        ("mi", "km", 1.609344),
        ("ft", "in", 12.0),
        ("yd", "m", 0.9144),
        ("in", "mm", 25.4),
        ("in", "cm", 2.54),
        ("km", "m", 1000.0),
        ("m", "cm", 100.0),
        ("mi", "ft", 5280.0),
        ("mi", "yd", 1760.0),
        ("ft", "m", 0.3048),
    ],
)
def test_known_pairs(src: str, dst: str, expected: float) -> None:
    """AC-6.2: known distance pairs convert within rel_tol=1e-12, abs_tol=1e-9."""
    result = convert(1, src, dst, registry=distance_registry())
    assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-9), result


def test_round_trips() -> None:
    """AC-6.3: 123.456 survives a round trip through every ordered pair of the 8 units."""
    registry = distance_registry()
    x = 123.456
    for src, dst in itertools.product(SYMBOLS, repeat=2):
        there = convert(x, src, dst, registry=registry)
        back = convert(there, dst, src, registry=registry)
        assert math.isclose(back, x, rel_tol=1e-12), (src, dst, back)


@pytest.mark.parametrize(
    ("spelling", "symbol"),
    [
        ("MI", "mi"),
        ("Km", "km"),
        ("mile", "mi"),
        ("Metre", "m"),
        ("inch", "in"),
        ("foot", "ft"),
        ("yard", "yd"),
        ("millimetre", "mm"),
        ("centimetre", "cm"),
        ("kilometre", "km"),
        ("meter", "m"),
        ("millimeter", "mm"),
        ("centimeter", "cm"),
        ("Kilometer", "km"),
    ],
)
def test_spellings(spelling: str, symbol: str) -> None:
    """AC-6.4: symbols in any case, UK names and US spellings resolve to the symbol's unit."""
    registry = distance_registry()
    for other in ("m", "ft"):
        assert convert(7.5, spelling, other, registry=registry) == convert(
            7.5, symbol, other, registry=registry
        )
        assert convert(7.5, other, spelling, registry=registry) == convert(
            7.5, other, symbol, registry=registry
        )


@pytest.mark.parametrize("spelling", ["feet", "miles", "inches", "meters", "nmi", "C"])
def test_not_a_distance_unit(spelling: str) -> None:
    """AC-6.5: plurals, unsupported and temperature units raise ConversionError naming them."""
    registry = distance_registry()
    with pytest.raises(ConversionError) as from_err:
        convert(1, spelling, "m", registry=registry)
    assert spelling in str(from_err.value)
    with pytest.raises(ConversionError) as to_err:
        convert(1, "m", spelling, registry=registry)
    assert spelling in str(to_err.value)


def test_empty_distance_unit() -> None:
    """AC-6.5: an empty unit string raises ConversionError with the distance registry."""
    registry = distance_registry()
    with pytest.raises(ConversionError):
        convert(1, "", "m", registry=registry)
    with pytest.raises(ConversionError):
        convert(1, "m", "", registry=registry)


@pytest.mark.parametrize(
    ("value", "src", "dst"), [(-1, "mi", "km"), (-0.5, "m", "ft"), (-1e-6, "mm", "m")]
)
def test_negative_distance_raises(value: float, src: str, dst: str) -> None:
    """AC-6.6: a negative distance raises ConversionError mentioning `negative`."""
    with pytest.raises(ConversionError) as err:
        convert(value, src, dst, registry=distance_registry())
    assert "negative" in str(err.value).lower()


@pytest.mark.parametrize(("value", "src", "dst"), [(0, "ft", "m"), (-0.0, "km", "mi")])
def test_zero_distance(value: float, src: str, dst: str) -> None:
    """AC-6.6: zero and -0.0 are allowed and return 0.0."""
    result = convert(value, src, dst, registry=distance_registry())
    assert result == 0.0


@pytest.mark.parametrize(
    ("value", "src", "dst"),
    [(float("nan"), "m", "ft"), (float("inf"), "m", "ft"), (1e308, "mi", "mm")],
)
def test_non_finite_and_overflow(value: float, src: str, dst: str) -> None:
    """AC-6.7: NaN, inf and overflowing results raise ConversionError, never inf or nan."""
    with pytest.raises(ConversionError):
        convert(value, src, dst, registry=distance_registry())


def test_default_registry_has_no_distance() -> None:
    """AC-6.8: the default registry knows no distance unit and still holds only temperature."""
    from conv.registry import build_default_registry

    distance_registry()  # the distance registry exists, yet stays out of the default
    with pytest.raises(ConversionError) as err:
        convert(1, "mi", "km")
    assert "mi" in str(err.value)
    assert [quantity.name for quantity in build_default_registry().quantities()] == ["temperature"]
