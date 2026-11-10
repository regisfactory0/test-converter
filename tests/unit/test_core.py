"""Unit tests: conversion details around clamping, overflow and non-temperature quantities."""

import math

import pytest

from conv import ConversionError, convert
from conv.core import MIN_BASE_TOLERANCE
from conv.registry import DEFAULT_REGISTRY, Quantity, Registry, Unit, build_default_registry


def _registry_with_amount() -> Registry:
    registry = build_default_registry()
    registry.register(
        Quantity(
            name="amount",
            base="u",
            units=(
                Unit(symbol="u", name="unit"),
                Unit(symbol="ku", name="kilounit", factor=1000.0),
            ),
            min_base=0.0,
        )
    )
    return registry


def test_tolerance_is_one_nanokelvin() -> None:
    assert MIN_BASE_TOLERANCE == 1e-9


@pytest.mark.parametrize("excess", [1e-12, 5e-10, 9e-10])
def test_base_just_below_absolute_zero_is_clamped_to_exactly_zero_kelvin(excess: float) -> None:
    assert convert(-excess, "K", "K") == 0.0
    assert convert(-excess, "K", "C") == convert(0, "K", "C")


def test_value_beyond_the_tolerance_below_absolute_zero_raises() -> None:
    with pytest.raises(ConversionError, match="absolute zero"):
        convert(-2e-9, "K", "K")


def test_float_rounding_at_absolute_zero_in_fahrenheit_does_not_raise() -> None:
    assert convert(-459.67, "F", "K") == pytest.approx(0.0, abs=1e-9)
    assert convert(-459.67, "F", "K") >= 0.0


def test_integer_input_returns_a_float() -> None:
    for result in (convert(100, "C", "F"), convert(5, "K", "K"), convert(0, "K", "C")):
        assert type(result) is float


def test_same_unit_by_symbol_and_name_returns_the_value() -> None:
    assert convert(37.5, "kelvin", "K") == pytest.approx(37.5, abs=1e-9)


def test_overflowing_result_raises_conversion_error() -> None:
    with pytest.raises(ConversionError):
        convert(1.7e308, "K", "F")


def test_large_finite_result_is_returned_finite() -> None:
    result = convert(1e300, "C", "F")
    assert math.isfinite(result)
    assert result == pytest.approx(1.8e300, rel=1e-12)


def test_default_registry_is_used_when_none_is_given() -> None:
    assert convert(100, "C", "F") == convert(100, "C", "F", registry=DEFAULT_REGISTRY)


def test_explicit_registry_is_used_instead_of_the_default() -> None:
    registry = Registry()
    with pytest.raises(ConversionError, match="'C'"):
        convert(1, "C", "F", registry=registry)


def test_non_temperature_minimum_message_names_the_quantity_not_absolute_zero() -> None:
    registry = _registry_with_amount()
    with pytest.raises(ConversionError) as err:
        convert(-1, "u", "ku", registry=registry)
    message = str(err.value)
    assert "amount" in message
    assert "absolute zero" not in message.lower()


def test_non_temperature_minimum_is_inclusive_and_scaled_by_factor() -> None:
    registry = _registry_with_amount()
    assert convert(0, "u", "ku", registry=registry) == 0.0
    with pytest.raises(ConversionError):
        convert(-0.001, "ku", "u", registry=registry)


def test_non_temperature_value_within_tolerance_is_clamped() -> None:
    registry = _registry_with_amount()
    assert convert(-5e-10, "u", "ku", registry=registry) == 0.0


def test_quantity_without_min_base_accepts_negative_values() -> None:
    registry = Registry()
    registry.register(
        Quantity(
            name="length",
            base="m",
            units=(
                Unit(symbol="m", name="metre"),
                Unit(symbol="km", name="kilometre", factor=1000.0),
            ),
        )
    )
    assert convert(-1, "km", "m", registry=registry) == -1000.0


def test_unknown_unit_message_keeps_the_spelling_as_given() -> None:
    with pytest.raises(ConversionError) as err:
        convert(1, "KelvinS", "C")
    assert "KelvinS" in str(err.value)


def test_non_finite_value_is_rejected_before_unit_lookup() -> None:
    with pytest.raises(ConversionError) as err:
        convert(float("nan"), "nope", "C")
    assert "nope" not in str(err.value)


def test_cross_quantity_message_says_different_quantities() -> None:
    registry = _registry_with_amount()
    with pytest.raises(ConversionError, match="different quantities"):
        convert(1, "u", "C", registry=registry)
