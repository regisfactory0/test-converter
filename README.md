# conv

`conv` is a small command-line tool and Python library that converts values
between units. It knows one quantity, temperature (Celsius, Fahrenheit,
Kelvin): `conv 100 C F` prints `212.0`. Units are data in a per-quantity
registry, so new quantities such as length, mass or volume can be added
without rewriting the CLI or the library.

It has no runtime dependencies and needs no network access.

## Install

Requires [uv](https://docs.astral.sh/uv/); uv provides Python 3.12 (pinned in
`.python-version`).

```sh
uv sync
```

## Run

```sh
uv run conv 100 C F      # 212.0
uv run conv --list       # known quantities and units
uv run conv --help
```

From Python:

```python
from conv import convert

convert(100, "C", "F")  # 212.0
```

Units are matched case-insensitively by symbol (`C`, `F`, `K`) or full name
(`celsius`, `fahrenheit`, `kelvin`). Invalid input prints a one-line
`conv: error: …` message on stderr and exits with code 1.

## Adding a quantity

A quantity is data: a `Quantity` holding its `Unit`s, both frozen dataclasses
imported from `conv.registry`. Every unit is affine to its quantity's base
unit: `base = value * factor + offset`.

`Unit` fields:

| Field | Default | Meaning |
|---|---|---|
| `symbol` | required | Short spelling, such as `km` |
| `name` | required | Full name, such as `kilometre` |
| `aliases` | `()` | Other accepted spellings |
| `factor` | `1.0` | Multiplier to the base unit |
| `offset` | `0.0` | Added after `factor`, for scales like Celsius |

`Quantity` fields:

| Field | Default | Meaning |
|---|---|---|
| `name` | required | Quantity name, such as `length` |
| `base` | required | Symbol of the base unit |
| `units` | required | Tuple of `Unit`s, in order; `conv --list` prints them in this order |
| `min_base` | `None` | Lowest allowed base value; temperature uses `0.0` (absolute zero) |

Register a quantity on a registry of your own and pass it to `convert`:

```python
from conv import convert
from conv.registry import Quantity, Registry, Unit

registry = Registry()
registry.register(
    Quantity(
        name="length",
        base="m",
        units=(
            Unit(symbol="m", name="metre", factor=1.0),
            Unit(symbol="km", name="kilometre", factor=1000.0),
        ),
    )
)

convert(1, "km", "m", registry=registry)  # 1000.0
```

`build_default_registry()` instead of `Registry()` gives a fresh registry that
already holds temperature.

### Built-in quantities

To make a quantity built in, register it in `build_default_registry()` in
`src/conv/registry.py`. `conv --list`, `conv <value> <from> <to>` and
`convert()` called without `registry=` then pick it up with no other code
change. A quantity registered at runtime on your own registry is used only
where that registry is passed, as `convert(..., registry=...)` or
`conv.cli.main(argv, registry)`; the `conv` command does not see it.

### Rules

- Symbols, names and aliases must be unique across the whole registry,
  compared case-insensitively. On a clash `register` raises `ValueError` and
  leaves the registry unchanged.
- Converting between units of different quantities raises
  `conv.ConversionError`, a subclass of `ValueError`.

### Changing the built-in list

Adding a built-in quantity changes the `conv --list` output, which AC-4.1 (in
`tests/acceptance/test_list.py`) pins to temperature only. AC-2.1 and the unit
tests in `tests/unit/test_registry.py` also pin the default registry to
temperature only. A change request that adds a built-in quantity must update
those expectations as part of its spec change.

## Test

```sh
uv run pytest                    # full suite
uv run pytest tests/acceptance   # acceptance tests only
uv run ruff check .              # lint
uv run ruff format --check .     # format check
```

## Configuration

None. `conv` reads no configuration files or environment variables.
