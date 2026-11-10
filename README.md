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

## Test

```sh
uv run pytest                    # full suite
uv run pytest tests/acceptance   # acceptance tests only
uv run ruff check .              # lint
uv run ruff format --check .     # format check
```

## Configuration

None. `conv` reads no configuration files or environment variables.
