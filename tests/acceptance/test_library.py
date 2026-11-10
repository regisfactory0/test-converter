"""Acceptance tests: the library conversion function and the unit registry."""

import math

import pytest

import conv
from conv import ConversionError, convert
from conv.registry import Quantity, Registry, Unit, build_default_registry

TOL = 1e-9


def _length() -> Quantity:
    return Quantity(
        name="length",
        base="m",
        units=(
            Unit(symbol="m", name="metre", aliases=("meter",), factor=1.0, offset=0.0),
            Unit(symbol="km", name="kilometre", aliases=("kilometer",), factor=1000.0, offset=0.0),
        ),
    )


# --- Library conversion function ---------------------------------------------


def test_convert_100_c_to_f() -> None:
    """AC-1.1: convert(100, "C", "F") returns 212.0 (int accepted, float returned)."""
    result = convert(100, "C", "F")
    assert isinstance(result, float)
    assert result == pytest.approx(212.0, abs=TOL)
    assert conv.convert is convert


@pytest.mark.parametrize(
    ("value", "src", "dst", "expected"),
    [
        (0, "C", "F", 32.0),
        (0, "C", "K", 273.15),
        (32, "F", "C", 0.0),
        (32, "F", "K", 273.15),
        (273.15, "K", "C", 0.0),
        (273.15, "K", "F", 32.0),
        (100, "C", "F", 212.0),
        (100, "C", "K", 373.15),
        (212, "F", "C", 100.0),
        (212, "F", "K", 373.15),
        (373.15, "K", "C", 100.0),
        (373.15, "K", "F", 212.0),
        (-40, "C", "F", -40.0),
        (-40, "F", "C", -40.0),
    ],
)
def test_convert_six_directions(value: float, src: str, dst: str, expected: float) -> None:
    """AC-1.2: all six directions match the known pairs within 1e-9."""
    assert math.isclose(convert(value, src, dst), expected, rel_tol=0.0, abs_tol=TOL)


def test_convert_same_unit_is_identity() -> None:
    """AC-1.3: convert(37.5, "K", "K") returns 37.5."""
    assert convert(37.5, "K", "K") == pytest.approx(37.5, abs=TOL)


@pytest.mark.parametrize(
    ("src", "dst"),
    [
        ("c", "f"),
        ("celsius", "Fahrenheit"),
        ("CELSIUS", "fahrenheit"),
        ("Celsius", "F"),
        ("C", "FAHRENHEIT"),
    ],
)
def test_convert_case_insensitive_and_full_names(src: str, dst: str) -> None:
    """AC-1.4: any letter case and full names resolve to the same units as the symbols."""
    assert convert(100, src, dst) == pytest.approx(212.0, abs=TOL)


@pytest.mark.parametrize(
    ("value", "src", "dst", "expected"),
    [
        (373.15, "Kelvin", "c", 100.0),
        (373.15, "kelvin", "celsius", 100.0),
        (212, "f", "KELVIN", 373.15),
        (300, "k", "kelvin", 300.0),
    ],
)
def test_convert_case_insensitive_kelvin(value: float, src: str, dst: str, expected: float) -> None:
    """AC-1.4: kelvin spellings resolve like the symbol K."""
    assert math.isclose(convert(value, src, dst), expected, rel_tol=0.0, abs_tol=TOL)


@pytest.mark.parametrize("unit", ["X", "°C", "kelvins", "degrees"])
def test_unknown_unit_raises_naming_it(unit: str) -> None:
    """AC-1.5: unknown units raise ConversionError (a ValueError) naming the unit."""
    assert issubclass(ConversionError, ValueError)
    with pytest.raises(ConversionError) as from_err:
        convert(10, unit, "C")
    assert unit in str(from_err.value)
    with pytest.raises(ConversionError) as to_err:
        convert(10, "C", unit)
    assert unit in str(to_err.value)


def test_empty_unit_raises() -> None:
    """AC-1.5: an empty unit string raises ConversionError."""
    with pytest.raises(ConversionError):
        convert(10, "", "C")
    with pytest.raises(ConversionError):
        convert(10, "C", "")


@pytest.mark.parametrize(
    ("value", "src", "dst"),
    [(-300, "C", "K"), (-1, "K", "C"), (-500, "F", "C"), (-273.16, "C", "F")],
)
def test_below_absolute_zero_raises(value: float, src: str, dst: str) -> None:
    """AC-1.6: values below absolute zero raise ConversionError mentioning absolute zero."""
    with pytest.raises(ConversionError) as err:
        convert(value, src, dst)
    assert "absolute zero" in str(err.value).lower()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_value_raises(value: float) -> None:
    """AC-1.7: NaN and infinite values raise ConversionError."""
    with pytest.raises(ConversionError):
        convert(value, "C", "F")


@pytest.mark.parametrize(
    ("value", "src", "dst", "expected"),
    [
        (0, "K", "C", -273.15),
        (-273.15, "C", "K", 0.0),
        (-459.67, "F", "K", 0.0),
        (-459.67, "F", "C", -273.15),
        (-273.15, "C", "F", -459.67),
    ],
)
def test_exactly_absolute_zero_is_allowed(
    value: float, src: str, dst: str, expected: float
) -> None:
    """AC-1.8: values exactly at absolute zero convert without error, within 1e-9."""
    assert math.isclose(convert(value, src, dst), expected, rel_tol=0.0, abs_tol=TOL)


def test_large_value_never_returns_inf() -> None:
    """AC-1.9: 1e300 C -> F returns a finite float; an overflow raises ConversionError."""
    result = convert(1e300, "C", "F")
    assert isinstance(result, float)
    assert math.isfinite(result)
    try:
        overflow = convert(1.7e308, "C", "F")
    except ConversionError:
        return
    assert math.isfinite(overflow)


# --- Unit registry per quantity ----------------------------------------------


def test_default_registry_holds_temperature() -> None:
    """AC-2.1: the registry holds exactly temperature, with units C, F, K."""
    quantities = build_default_registry().quantities()
    assert [q.name for q in quantities] == ["temperature"]
    temperature = quantities[0]
    assert [u.symbol for u in temperature.units] == ["C", "F", "K"]
    assert [u.name for u in temperature.units] == ["celsius", "fahrenheit", "kelvin"]
    for unit in temperature.units:
        assert isinstance(unit.aliases, tuple)
    assert temperature.base == "K"
    assert temperature.min_base == 0.0


def test_new_quantity_converts_through_same_code() -> None:
    """AC-2.2: a dummy length quantity on a fresh registry converts 1 km to 1000.0 m."""
    registry = Registry()
    registry.register(_length())
    assert convert(1, "km", "m", registry=registry) == pytest.approx(1000.0, abs=TOL)
    assert convert(500, "m", "kilometre", registry=registry) == pytest.approx(0.5, abs=TOL)


def test_cross_quantity_conversion_raises() -> None:
    """AC-2.3: converting between units of different quantities raises ConversionError."""
    registry = build_default_registry()
    registry.register(_length())
    assert convert(100, "C", "F", registry=registry) == pytest.approx(212.0, abs=TOL)
    for src, dst in (("m", "C"), ("C", "m")):
        with pytest.raises(ConversionError) as err:
            convert(1, src, dst, registry=registry)
        assert "quantit" in str(err.value).lower()


@pytest.mark.parametrize(
    "unit",
    [
        Unit(symbol="M", name="mile"),  # symbol clashes with symbol m
        Unit(symbol="x", name="ex", aliases=("KM",)),  # alias clashes with symbol km
        Unit(symbol="Meter", name="other"),  # symbol clashes with alias meter
        Unit(symbol="y", name="why", aliases=("Kilometer",)),  # alias clashes with alias
        Unit(symbol="c", name="cubit"),  # symbol clashes with temperature's C
        Unit(symbol="z", name="zed", aliases=("CELSIUS",)),  # alias clashes with name celsius
    ],
)
def test_duplicate_symbol_or_alias_raises(unit: Unit) -> None:
    """AC-2.4: registering a unit whose symbol or alias already exists raises ValueError."""
    registry = build_default_registry()
    registry.register(_length())
    clash = Quantity(name="dummy", base=unit.symbol, units=(unit,))
    with pytest.raises(ValueError):
        registry.register(clash)


def test_duplicate_within_one_quantity_raises() -> None:
    """AC-2.4: two units of one new quantity sharing a symbol (any case) raise ValueError."""
    clash = Quantity(
        name="dummy",
        base="a",
        units=(Unit(symbol="a", name="alpha"), Unit(symbol="A", name="big alpha")),
    )
    with pytest.raises(ValueError):
        Registry().register(clash)
