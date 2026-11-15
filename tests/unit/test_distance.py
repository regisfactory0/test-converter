"""Unit tests: the distance quantity's data and its negative-value rule."""

import math

import pytest

from conv import ConversionError, convert
from conv.core import MIN_BASE_TOLERANCE
from conv.registry import (
    DEFAULT_REGISTRY,
    DISTANCE_REGISTRY,
    Quantity,
    Registry,
    Unit,
    build_default_registry,
    build_distance_registry,
)

FACTORS = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
    "in": 0.0254,
    "ft": 0.3048,
    "yd": 0.9144,
    "mi": 1609.344,
}


def _unit_by_symbol(symbol: str) -> Unit:
    found = DISTANCE_REGISTRY.find(symbol)
    assert found is not None
    return found[1]


def test_distance_registry_has_one_quantity_with_base_metre() -> None:
    (quantity,) = build_distance_registry().quantities()
    assert quantity.name == "distance"
    assert quantity.base == "m"


def test_distance_units_are_in_the_documented_order() -> None:
    (quantity,) = build_distance_registry().quantities()
    assert [u.symbol for u in quantity.units] == list(FACTORS)
    assert [u.name for u in quantity.units] == [
        "millimetre",
        "centimetre",
        "metre",
        "kilometre",
        "inch",
        "foot",
        "yard",
        "mile",
    ]


@pytest.mark.parametrize(("symbol", "factor"), FACTORS.items())
def test_distance_unit_has_exact_factor_and_no_offset(symbol: str, factor: float) -> None:
    unit = _unit_by_symbol(symbol)
    assert unit.factor == factor
    assert unit.offset == 0.0


def test_us_spellings_are_aliases_of_metric_units_only() -> None:
    (quantity,) = build_distance_registry().quantities()
    aliases = {u.symbol: u.aliases for u in quantity.units}
    assert aliases["mm"] == ("millimeter",)
    assert aliases["cm"] == ("centimeter",)
    assert aliases["m"] == ("meter",)
    assert aliases["km"] == ("kilometer",)
    for symbol in ("in", "ft", "yd", "mi"):
        assert aliases[symbol] == ()


def test_each_call_builds_a_fresh_registry() -> None:
    first = build_distance_registry()
    second = build_distance_registry()
    assert first is not second
    first.register(Quantity(name="extra", base="x", units=(Unit(symbol="x", name="ex"),)))
    assert [q.name for q in second.quantities()] == ["distance"]


def test_module_level_distance_registry_holds_only_distance() -> None:
    assert [q.name for q in DISTANCE_REGISTRY.quantities()] == ["distance"]
    assert DISTANCE_REGISTRY.find("mi") is not None
    assert DISTANCE_REGISTRY.find("C") is None


def test_default_registry_stays_temperature_only() -> None:
    for registry in (DEFAULT_REGISTRY, build_default_registry()):
        assert [q.name for q in registry.quantities()] == ["temperature"]
        assert registry.find("mi") is None


@pytest.mark.parametrize("value", [-1.0, -0.5, -1e-6, -1e-12, -1e-300])
def test_negative_distance_raises_with_negative_in_the_message(value: float) -> None:
    with pytest.raises(ConversionError, match="negative"):
        convert(value, "m", "ft", registry=build_distance_registry())


def test_negative_distance_in_a_large_unit_raises() -> None:
    with pytest.raises(ConversionError, match="negative"):
        convert(-1, "mi", "km", registry=DISTANCE_REGISTRY)


@pytest.mark.parametrize("value", [0, 0.0, -0.0])
def test_zero_distance_is_allowed_and_returns_zero(value: float) -> None:
    result = convert(value, "km", "mi", registry=DISTANCE_REGISTRY)
    assert result == 0.0
    assert isinstance(result, float)


def test_negative_distance_message_does_not_mention_absolute_zero() -> None:
    with pytest.raises(ConversionError) as excinfo:
        convert(-1, "m", "km", registry=DISTANCE_REGISTRY)
    assert "absolute zero" not in str(excinfo.value)


def test_temperature_below_absolute_zero_keeps_its_message() -> None:
    with pytest.raises(ConversionError, match="below absolute zero"):
        convert(-300, "C", "K")


def test_temperature_keeps_the_nanokelvin_tolerance_and_clamp() -> None:
    assert convert(-1e-10, "K", "C") == convert(0, "K", "C")
    with pytest.raises(ConversionError, match="below absolute zero"):
        convert(-2e-9, "K", "C")


def test_temperature_quantity_leaves_tolerance_to_the_core_default() -> None:
    (quantity,) = build_default_registry().quantities()
    assert quantity.min_tolerance is None
    assert MIN_BASE_TOLERANCE == 1e-9


def _amount_registry(
    min_tolerance: float | None = None, below_min_message: str | None = None
) -> Registry:
    registry = Registry()
    registry.register(
        Quantity(
            name="amount",
            base="u",
            units=(Unit(symbol="u", name="unit"), Unit(symbol="k", name="kilo", factor=1000.0)),
            min_base=0.0,
            min_tolerance=min_tolerance,
            below_min_message=below_min_message,
        )
    )
    return registry


def test_minimum_without_message_uses_the_generic_fallback_naming_the_quantity() -> None:
    with pytest.raises(ConversionError) as excinfo:
        convert(-1, "u", "k", registry=_amount_registry())
    assert str(excinfo.value) == "value is below the minimum for amount"


def test_custom_message_replaces_the_generic_one() -> None:
    registry = _amount_registry(below_min_message="too small")
    with pytest.raises(ConversionError) as excinfo:
        convert(-1, "u", "k", registry=registry)
    assert str(excinfo.value) == "too small"


def test_unset_tolerance_defaults_to_one_nano_unit_of_base() -> None:
    registry = _amount_registry()
    assert convert(-5e-10, "u", "k", registry=registry) == 0.0
    with pytest.raises(ConversionError):
        convert(-2e-9, "u", "k", registry=registry)


def test_zero_tolerance_rejects_what_the_default_would_clamp() -> None:
    registry = _amount_registry(min_tolerance=0.0)
    with pytest.raises(ConversionError):
        convert(-5e-10, "u", "k", registry=registry)


def test_wider_tolerance_clamps_to_the_minimum() -> None:
    registry = _amount_registry(min_tolerance=0.5)
    assert convert(-0.25, "u", "k", registry=registry) == 0.0
    with pytest.raises(ConversionError):
        convert(-0.75, "u", "k", registry=registry)


@pytest.mark.parametrize("value", [math.nan, math.inf, 1e308])
def test_distance_overflow_and_non_finite_input_are_rejected(value: float) -> None:
    with pytest.raises(ConversionError):
        convert(value, "mi", "mm", registry=DISTANCE_REGISTRY)
