"""Unit tests: registration and lookup details of the registry."""

import pytest

from conv.registry import (
    DEFAULT_REGISTRY,
    Quantity,
    Registry,
    Unit,
    build_default_registry,
)


def _quantity(name: str, *units: Unit) -> Quantity:
    return Quantity(name=name, base=units[0].symbol, units=units)


def test_empty_registry_has_no_quantities_and_finds_nothing() -> None:
    registry = Registry()
    assert registry.quantities() == ()
    assert registry.find("C") is None


def test_quantities_keep_registration_order() -> None:
    registry = Registry()
    registry.register(_quantity("zeta", Unit(symbol="z", name="zed")))
    registry.register(_quantity("alpha", Unit(symbol="a", name="ay")))
    registry.register(_quantity("mid", Unit(symbol="m", name="em")))
    assert [q.name for q in registry.quantities()] == ["zeta", "alpha", "mid"]


def test_units_keep_their_order_in_default_temperature() -> None:
    (temperature,) = build_default_registry().quantities()
    assert [u.symbol for u in temperature.units] == ["C", "F", "K"]
    assert all(unit.aliases == () for unit in temperature.units)


@pytest.mark.parametrize("spelling", ["C", "c", "celsius", "Celsius", "CELSIUS"])
def test_find_resolves_symbol_and_name_in_any_case(spelling: str) -> None:
    found = build_default_registry().find(spelling)
    assert found is not None
    quantity, unit = found
    assert quantity.name == "temperature"
    assert unit.symbol == "C"


def test_find_resolves_aliases_in_any_case() -> None:
    registry = Registry()
    registry.register(_quantity("length", Unit(symbol="m", name="metre", aliases=("meter",))))
    found = registry.find("METER")
    assert found is not None
    assert found[1].symbol == "m"


@pytest.mark.parametrize("spelling", ["", "X", "°C", "kelvins", "degrees"])
def test_find_returns_none_for_unknown_spelling(spelling: str) -> None:
    assert build_default_registry().find(spelling) is None


def test_default_registry_is_a_built_registry_with_temperature_only() -> None:
    assert [q.name for q in DEFAULT_REGISTRY.quantities()] == ["temperature"]


def test_build_default_registry_returns_a_fresh_registry_each_call() -> None:
    first = build_default_registry()
    second = build_default_registry()
    assert first is not second
    assert first is not DEFAULT_REGISTRY
    first.register(_quantity("length", Unit(symbol="m", name="metre")))
    assert [q.name for q in second.quantities()] == ["temperature"]
    assert [q.name for q in DEFAULT_REGISTRY.quantities()] == ["temperature"]
    assert second.find("m") is None


@pytest.mark.parametrize(
    "clashing",
    [
        Unit(symbol="M", name="mile"),
        Unit(symbol="x", name="METRE"),
        Unit(symbol="x", name="ex", aliases=("Meter",)),
        Unit(symbol="Metre", name="ex"),
        Unit(symbol="x", name="ex", aliases=("m",)),
    ],
)
def test_register_rejects_any_key_clashing_with_an_existing_unit(clashing: Unit) -> None:
    registry = Registry()
    registry.register(_quantity("length", Unit(symbol="m", name="metre", aliases=("meter",))))
    with pytest.raises(ValueError):
        registry.register(_quantity("other", clashing))


@pytest.mark.parametrize(
    "second",
    [
        Unit(symbol="A", name="beta"),
        Unit(symbol="b", name="ALPHA"),
        Unit(symbol="b", name="beta", aliases=("a",)),
        Unit(symbol="b", name="beta", aliases=("ALPHA",)),
        Unit(symbol="Alpha", name="beta"),
    ],
)
def test_register_rejects_clash_between_units_of_the_same_quantity(second: Unit) -> None:
    registry = Registry()
    with pytest.raises(ValueError):
        registry.register(_quantity("dummy", Unit(symbol="a", name="alpha"), second))


def test_register_rejects_the_same_quantity_registered_twice() -> None:
    registry = Registry()
    quantity = _quantity("length", Unit(symbol="m", name="metre"))
    registry.register(quantity)
    with pytest.raises(ValueError):
        registry.register(quantity)


def test_rejected_registration_leaves_registry_unchanged() -> None:
    registry = build_default_registry()
    before = registry.quantities()
    clashing = _quantity(
        "mixed",
        Unit(symbol="ok", name="fine"),
        Unit(symbol="also", name="good", aliases=("KELVIN",)),
    )
    with pytest.raises(ValueError):
        registry.register(clashing)
    assert registry.quantities() == before
    assert registry.find("ok") is None
    assert registry.find("fine") is None
    assert registry.find("also") is None
    found = registry.find("kelvin")
    assert found is not None
    assert found[0].name == "temperature"


def test_rejected_registration_does_not_block_a_later_valid_one() -> None:
    registry = build_default_registry()
    with pytest.raises(ValueError):
        registry.register(
            _quantity("bad", Unit(symbol="ok", name="fine"), Unit(symbol="c", name="clash"))
        )
    registry.register(_quantity("good", Unit(symbol="ok", name="fine")))
    assert [q.name for q in registry.quantities()] == ["temperature", "good"]


def test_unit_whose_symbol_and_name_are_the_same_word_does_not_clash_with_itself() -> None:
    registry = Registry()
    registry.register(_quantity("count", Unit(symbol="Item", name="item", aliases=("ITEM",))))
    found = registry.find("item")
    assert found is not None
    assert found[0].name == "count"
