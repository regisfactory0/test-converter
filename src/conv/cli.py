"""The ``conv`` command line."""

import math
import sys

from conv.core import ConversionError, convert
from conv.registry import DEFAULT_REGISTRY, Quantity, Registry

__all__ = ["convert", "main"]

USAGE = "usage: conv <value> <from> <to> | conv --list"
HELP = f"""{USAGE}

Convert a value between units, e.g. `conv 100 C F` prints 212.0.

arguments:
  value       the number to convert (negative values are allowed)
  from        the unit to convert from, by symbol or name (C, celsius)
  to          the unit to convert to

options:
  -h, --help  show this help and exit
  --list      list the known quantities and their units and exit"""


def _parse_value(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise ConversionError(f"invalid number: {text!r}") from None
    if not math.isfinite(value):
        raise ConversionError(f"invalid number: {text!r}")
    return value


def _usage_problem(args: list[str]) -> str | None:
    for arg in args:
        if arg.startswith("-") and not _looks_numeric(arg):
            return f"unrecognized option: {arg!r}"
    if len(args) != 3:
        return f"expected 3 arguments (value, from, to), got {len(args)}"
    return None


def _looks_numeric(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def _format(result: float) -> str:
    rounded = round(result, 6)
    if rounded == 0:
        rounded = 0.0
    return repr(rounded)


def _quantity_line(quantity: Quantity) -> str:
    units = ", ".join(f"{unit.symbol} ({unit.name})" for unit in quantity.units)
    return f"{quantity.name}: {units}"


def _list(registry: Registry) -> None:
    for quantity in sorted(registry.quantities(), key=lambda quantity: quantity.name):
        print(_quantity_line(quantity))


def main(argv: list[str] | None = None, registry: Registry | None = None) -> int:
    """Run ``conv`` with ``argv`` (default: the process arguments); return the exit code."""
    args = sys.argv[1:] if argv is None else list(argv)
    if any(arg in ("-h", "--help") for arg in args):
        print(HELP)
        return 0
    if "--list" in args:
        if len(args) != 1:
            print(USAGE, file=sys.stderr)
            print("conv: error: --list takes no other arguments", file=sys.stderr)
            return 1
        _list(DEFAULT_REGISTRY if registry is None else registry)
        return 0
    problem = _usage_problem(args)
    if problem is not None:
        print(USAGE, file=sys.stderr)
        print(f"conv: error: {problem}", file=sys.stderr)
        return 1
    value_text, from_unit, to_unit = args
    try:
        result = convert(_parse_value(value_text), from_unit, to_unit, registry=registry)
    except ConversionError as error:
        print(f"conv: error: {error}", file=sys.stderr)
        return 1
    print(_format(result))
    return 0
