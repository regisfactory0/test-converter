"""Conversion between units of a registry."""

import math

from conv.registry import DEFAULT_REGISTRY, Quantity, Registry, Unit

MIN_BASE_TOLERANCE = 1e-9


class ConversionError(ValueError):
    """A value or unit that cannot be converted."""


def _lookup(registry: Registry, spelling: str) -> tuple[Quantity, Unit]:
    found = registry.find(spelling)
    if found is None:
        raise ConversionError(f"unknown unit: {spelling!r}")
    return found


def _below_minimum_message(quantity: Quantity) -> str:
    if quantity.name == "temperature":
        return "value is below absolute zero"
    return f"value is below the minimum for {quantity.name}"


def convert(value: float, from_unit: str, to_unit: str, registry: Registry | None = None) -> float:
    """Convert ``value`` from ``from_unit`` to ``to_unit``.

    Raises ``ConversionError`` for a non-finite value, an unknown unit, units of different
    quantities, a value below the quantity's minimum, or a result that overflows.
    """
    if registry is None:
        registry = DEFAULT_REGISTRY
    if not math.isfinite(value):
        raise ConversionError(f"value is not finite: {value!r}")
    source_quantity, source = _lookup(registry, from_unit)
    target_quantity, target = _lookup(registry, to_unit)
    if source_quantity is not target_quantity:
        raise ConversionError(
            f"units are of different quantities: {from_unit!r} is {source_quantity.name}, "
            f"{to_unit!r} is {target_quantity.name}"
        )
    base = value * source.factor + source.offset
    minimum = source_quantity.min_base
    if minimum is not None and base < minimum:
        if base < minimum - MIN_BASE_TOLERANCE:
            raise ConversionError(_below_minimum_message(source_quantity))
        base = minimum
    result = float((base - target.offset) / target.factor)
    if not math.isfinite(result):
        raise ConversionError(f"result overflows: {value!r} {from_unit} in {to_unit}")
    return result
