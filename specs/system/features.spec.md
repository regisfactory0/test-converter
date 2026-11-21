# Features — test-converter

As-built behaviour of `conv`, feature by feature. Layers, boundaries, public
names and the structural decisions are in
[architecture.spec.md](architecture.spec.md); this file does not repeat them.
Criterion ids (`AC-…`) are kept because tests, the README and the architecture
spec cite them. Every criterion listed here has passed unless it appears under
[Still to check](#still-to-check).

## Features

### Temperature conversion

`conv.convert(value, from_unit, to_unit, registry=None) -> float` converts
through the quantity's base unit; `registry=None` means `DEFAULT_REGISTRY`. In
order, `convert`:

1. rejects a non-finite `value` with `ConversionError`;
2. looks up both units with `Registry.find`; an unknown spelling, including
   `""`, raises `ConversionError` whose message contains the spelling as given;
3. raises `ConversionError` saying the units are of different quantities when
   they belong to different quantities;
4. computes `base = value * factor + offset`, then applies the quantity's
   minimum (see [Per-quantity minimum](#per-quantity-minimum));
5. computes `(base - offset) / factor` for the target unit, and raises
   `ConversionError` if the result is not finite (overflow);
6. returns a `float`, also for an `int` input, at full precision. Only the CLI
   rounds.

The temperature quantity (base `K`, `min_base = 0.0`) is built by
`build_default_registry()`, units in this order, no aliases:

| Symbol | Name | Factor | Offset |
|---|---|---|---|
| `C` | `celsius` | 1 | 273.15 |
| `F` | `fahrenheit` | 5/9 | 459.67 · 5/9 |
| `K` | `kelvin` | 1 | 0 |

Accepted spellings are exactly those symbols and names, in any letter case. A
degree sign (`°C`), plurals (`kelvins`, `degrees`) and forms like `degC` are
unknown units. Other scales (Rankine, Réaumur) are not supported.

Decisions:

| Decision | Why |
|---|---|
| Absolute zero has a 1e-9 K tolerance, and a base inside it is clamped to 0 K | Float rounding would otherwise reject exactly 0 K given as `-459.67 F` |
| `convert` never returns `inf`; overflow is a `ConversionError` | Callers and the CLI handle one error type, never a non-finite result |
| Error wording is free beyond naming the offending unit and mentioning absolute zero | Tests check those words only |

Note on AC-1.1: `convert(100, "C", "F")` returns `211.99999999999997`, within
1e-9 of `212.0` but not bit-exact. AC-1.2 sets the tolerance, and the CLI's
rounding makes `conv 100 C F` print `212.0`.

| Id | Criterion |
|---|---|
| AC-1.1 | `convert(100, "C", "F")` returns `212.0` (within the AC-1.2 tolerance) |
| AC-1.2 | All six directions match 0 °C = 32 °F = 273.15 K, 100 °C = 212 °F = 373.15 K, −40 °C = −40 °F within an absolute 1e-9 |
| AC-1.3 | `convert(37.5, "K", "K")` returns `37.5` |
| AC-1.4 | Any letter case and the full names (`c`, `celsius`, `Fahrenheit`, `kelvin`) resolve like the symbols |
| AC-1.5 | `X`, `""`, `°C`, `kelvins`, `degrees` raise `ConversionError` (a `ValueError`) naming the spelling |
| AC-1.6 | A value below absolute zero (`-300 C → K`, `-1 K → C`) raises `ConversionError` mentioning absolute zero |
| AC-1.7 | `nan` and `inf` raise `ConversionError` |
| AC-1.8 | Exactly absolute zero in each unit (`0 K → C`, `-273.15 C → K`, `-459.67 F → K`) gives `-273.15`, `0.0`, `0.0` within 1e-9, no error |
| AC-1.9 | `1e300 C → F` returns a finite float or raises `ConversionError`, never `inf` |

### Unit registry

Units are data: `Unit`, `Quantity` and `Registry` in `conv.registry`. A
`Registry` starts empty; `register(quantity)` adds a quantity and its units,
`quantities()` returns them in registration order, `find(spelling)` looks a
unit up case-insensitively by symbol, name or alias.

Every lookup key of a unit (symbol, name and aliases, compared
case-insensitively) is unique across the whole registry, including the other
units of the same quantity. A clash raises `ValueError` and leaves the
registry unchanged. `build_default_registry()` returns a fresh registry
holding exactly `temperature`; `DEFAULT_REGISTRY` is built from it at import
time.

Decision: units are affine (`factor` and `offset`), not a temperature special
case, because linear units are the same model with offset 0. AC-2.2 proves it
with a quantity that is not built in.

| Id | Criterion |
|---|---|
| AC-2.1 | The default registry holds exactly `temperature`, with units `C`, `F`, `K` (symbol, name, aliases) |
| AC-2.2 | A `length` quantity (`m`, `km` factor 1000) registered on a fresh registry converts `1 km → m` to `1000.0` with no library or CLI change |
| AC-2.3 | Converting between units of different quantities raises `ConversionError` saying they are of different quantities |
| AC-2.4 | Registering a symbol or alias that already exists (case-insensitive) raises `ValueError` |

### Per-quantity minimum

A `Quantity` may carry `min_base`, `min_tolerance` and `below_min_message`.
When `base < min_base - tolerance`, `convert` raises `ConversionError` with
`below_min_message` (a generic message when it is `None`). A base inside the
tolerance is clamped to `min_base`. `min_tolerance = None` means the core's
default, `MIN_BASE_TOLERANCE = 1e-9` in `conv.core`.

| Quantity | `min_base` | Tolerance | Message |
|---|---|---|---|
| temperature | `0.0` | default (1e-9 K) | `value is below absolute zero` |
| distance | `0.0` | `0.0` | `value is negative` |

Constraint: temperature keeps its absolute-zero message, tolerance and clamp
(AC-1.6, AC-1.8) whatever another quantity needs.

### CLI conversion

`conv <value> <from> <to>` (entry point `conv.cli.main`) parses the value,
calls `convert` and prints the result. Interactive mode, stdin or file input,
several values at once, precision flags and localisation are not supported.

- **Parsing.** The CLI parses the value with `float()` itself, so a bad number
  gives exactly one stderr line. A negative number such as `-40` is a value,
  not an option. NaN and infinity are invalid numbers.
- **Output.** `round(result, 6)`, printed as its `repr`: trailing zeros
  dropped, at least one decimal kept; `-0.0` prints as `0.0` (`conv 32 F C`).
- **Errors.** Every invalid input prints one `conv: error: <message>` line on
  stderr and exits 1, never a traceback; the message names the offending value
  or unit. Wrong argument counts and unknown options add a short usage line
  before it. A `ConversionError` from `convert`, including overflow
  (`conv 1e308 C F`), becomes that line.
- **Exit codes.** `main` returns the exit code instead of calling `sys.exit`;
  `--help` prints usage on stdout and returns 0.
- `registry=None` means the library's default registry and is passed to
  `convert` unchanged.

Decisions:

| Decision | Why |
|---|---|
| Exit 1 for every invalid input, including argument count (not argparse's 2) | One failure code for scripts; fixed in `CLAUDE.md` |
| Value parsed by the CLI with `float()`, not a parser type converter | A parser's own error would add lines; AC-3.5 requires exactly one |
| Round to 6 places in the CLI only | Hides float noise (`98.60000000000001`) without losing precision for library callers |

Product constraints checked with this feature: `conv 100 C F` finishes in
under 0.5 s; no runtime dependencies (`dependencies = []` in
`pyproject.toml`); no network access and no file writes.

| Id | Criterion |
|---|---|
| AC-3.1 | `conv 100 C F` prints exactly `212.0\n`, empty stderr, exit 0 |
| AC-3.2 | `conv 100 F C` prints `37.777778\n` (6 places, `repr` of the rounded float) |
| AC-3.3 | `conv -40 C F` prints `-40.0\n`, exit 0 |
| AC-3.4 | `conv 0 C K` prints `273.15\n`; `conv 1e3 K C` prints `726.85\n` |
| AC-3.5 | `abc`, `""`, `nan`, `inf` as the value: one `conv: error:` line, empty stdout, exit 1 |
| AC-3.6 | `conv 10 C X`: one `conv: error:` line naming `X`, exit 1 |
| AC-3.7 | `conv -500 F C`: one `conv: error:` line mentioning absolute zero, exit 1 |
| AC-3.8 | No, one, two or four arguments: a usage line plus a `conv: error:` line, exit 1 |
| AC-3.9 | `conv --help` prints usage on stdout, exit 0 |
| AC-3.10 | `main(argv)` returns the exit code and calls the library's `convert` (a test patches `conv.cli.convert`) |
| AC-3.11 | No invalid input prints a traceback |

### Listing units (`--list`)

`conv --list` prints one line per quantity of the registry in use, sorted by
quantity name, units in registration order:
`<quantity>: <symbol> (<name>), <symbol> (<name>), …`. It shows no aliases,
factors or offsets, and has no filter or machine-readable format. `--list`
with any conversion argument, in either order, is an error (exit 1).

| Id | Criterion |
|---|---|
| AC-4.1 | `conv --list` prints exactly `temperature: C (celsius), F (fahrenheit), K (kelvin)\n`, exit 0 |
| AC-4.2 | With an extra quantity in a test registry passed to `main`, each quantity is on its own line, alphabetical by name, units in registration order |
| AC-4.3 | `conv --list 1 C F`: a `conv: error:` line, exit 1 |

### Distance conversion

`conv.registry.build_distance_registry()` returns a fresh registry holding only
`distance` (base `m`); `DISTANCE_REGISTRY` is built from it at import time.
Units are linear (offset 0), in this order:

| Symbol | Name | Aliases | Factor to metres |
|---|---|---|---|
| `mm` | millimetre | `millimeter` | 0.001 |
| `cm` | centimetre | `centimeter` | 0.01 |
| `m` | metre | `meter` | 1 |
| `km` | kilometre | `kilometer` | 1000 |
| `in` | inch | — | 0.0254 |
| `ft` | foot | — | 0.3048 |
| `yd` | yard | — | 0.9144 |
| `mi` | mile | — | 1609.344 |

Every negative distance is rejected with a message containing `negative`, with
no tolerance; `0` and `-0.0` are allowed and give `0.0`. Plurals (`feet`),
compound input (`5 ft 3 in`) and other units (nautical mile, survey foot, …)
are not supported. The default registry does not hold distance.

Decisions:

| Decision | Why |
|---|---|
| Exact international factors (1959 yard and pound agreement) | They are exact by definition, so only float rounding separates results from the true value |
| UK spellings as `name`, US spellings as aliases, imperial units without aliases | One listed name per unit; US users still type `meter` |
| No tolerance below zero for distance | A negative length has no rounding excuse, unlike 0 K reached through `F` |
| Plurals rejected, not aliased | A clear unknown-unit error naming the spelling; aliases can be added later as data |

| Id | Criterion |
|---|---|
| AC-6.1 | `build_distance_registry()` returns a fresh registry with exactly `distance`, base `m`, units `mm`, `cm`, `m`, `km`, `in`, `ft`, `yd`, `mi` in that order with the names above |
| AC-6.2 | `1` converts `mi→km` 1.609344, `ft→in` 12, `yd→m` 0.9144, `in→mm` 25.4, `in→cm` 2.54, `km→m` 1000, `m→cm` 100, `mi→ft` 5280, `mi→yd` 1760, `ft→m` 0.3048, within `rel_tol=1e-12, abs_tol=1e-9` |
| AC-6.3 | `123.456` converted between every ordered pair of distance units and back returns within `rel_tol=1e-12` |
| AC-6.4 | Any letter case of the symbols, the names and the US spellings resolves like the symbols |
| AC-6.5 | `feet`, `miles`, `inches`, `meters`, `""`, `nmi`, `C` raise `ConversionError` naming the spelling |
| AC-6.6 | `-1 mi`, `-0.5 m`, `-1e-6 mm` raise `ConversionError` containing `negative`; `0 ft` and `-0.0 km` return `0.0` |
| AC-6.7 | `nan`, `inf` and `1e308 mi → mm` raise `ConversionError`, never `inf` or `nan` |
| AC-6.8 | Without `registry=`, `convert(1, "mi", "km")` raises `ConversionError` naming `mi`; the default registry still holds exactly `temperature` |

### Distance mode in the CLI (`-d` / `--distance`)

`-d` / `--distance` anywhere on the command line is taken out of the
arguments, and the rest runs unchanged with the distance registry in place of
the default one: conversion, `--list` and `--help`. All
[CLI conversion](#cli-conversion) rules carry over, including a dash-prefixed
number after the flag (`-d -3 ft m`) being a value. The negative-distance
error comes from `convert`. Without the flag, `conv` and `conv --list` behave
exactly as before, and a distance unit is an unknown unit. `--help` mentions
`-d, --distance`.

Decision: distance mode is a flag that swaps the registry, not a merge into
the default registry, so plain `conv` and `conv --list` keep their pinned
behaviour (see the `Why` table in
[architecture.spec.md](architecture.spec.md)).

The README has a `## Distance` section with a `conv --distance 1 mi km`
example, `conv -d --list` and its output, and a runnable Python example using
`build_distance_registry()`.

| Id | Criterion |
|---|---|
| AC-7.1 | `conv --distance 1 mi km` and `conv -d 1 mi km` print exactly `1.609344\n`, empty stderr, exit 0 |
| AC-7.2 | `conv -d 100 km mi`, `1 m ft`, `5280 ft mi`, `1 ft in`, `1 yd cm` print `62.137119`, `3.28084`, `1.0`, `12.0`, `91.44`, exit 0 |
| AC-7.3 | `conv -d -3 ft m`: one `conv: error:` line containing `negative`, empty stdout, no traceback, exit 1; `conv -d 0 ft m` prints `0.0\n`, exit 0 |
| AC-7.4 | `conv 1 mi km --distance` prints `1.609344\n`, exit 0 |
| AC-7.5 | `conv -d abc m ft`, `-d nan m ft`, `-d 1 C F` (naming `C`), `-d 1e308 mi mm`: one `conv: error:` line, empty stdout, no traceback, exit 1 |
| AC-7.6 | `conv -d`, `conv -d 1 m`, `conv -d 1 m ft in`: a usage line plus a `conv: error:` line, exit 1 |
| AC-7.7 | `conv --distance --list` and `conv -d --list` print exactly `distance: mm (millimetre), cm (centimetre), m (metre), km (kilometre), in (inch), ft (foot), yd (yard), mi (mile)\n`, exit 0; `conv -d --list 1 m ft` is an error, exit 1 |
| AC-7.8 | `conv --help` mentions `--distance`, exit 0 |
| AC-7.9 | `main(["--distance", "1", "mi", "km"])` with `convert` patched calls it once with a registry whose only quantity is `distance`, and returns 0 |
| AC-D.1 | The README still has its "Adding a quantity" section |
| AC-D.2 | The README has a "Distance" section with `conv --distance` usage, `conv -d --list` and the `build_distance_registry()` library call |

### Listing every unit (`--units`)

`conv --units` prints the quantities of both the registry for runs without
the flag (`registry`, default `DEFAULT_REGISTRY`) and the distance registry
(`distance_registry`, default `DISTANCE_REGISTRY`), sorted by quantity name:
a `<quantity>:` line, then one `  <symbol> (<name>)` line per unit (two-space
indent) in registration order. Aliases are not listed. With `-d` the output is
the same full list. Once `-d` / `--distance` is removed, `--units` must be the
only argument left; otherwise a usage line plus one `conv: error:` line, exit 1
(this also covers `--units --list` in either order).

Decisions:

| Decision | Why |
|---|---|
| `--units` reads both registries whatever `-d` says | `-d` swaps the registry, so `conv -d --units` would otherwise list only distance |
| The distance quantity is listed as `distance`, not `length` | It is the product's existing name; no rename |
| A quantity name present in both registries is printed as two groups, in the order the registries are given | Not reachable in the product; the spec left the merge to the developer |

`--list` and `-d --list` are unchanged by this feature (AC-4.1, AC-7.7).

| Id | Criterion |
|---|---|
| AC-8.1 | `conv --units` and `conv -d --units` print exactly a `distance:` group (`mm`, `cm`, `m`, `km`, `in`, `ft`, `yd`, `mi` with their names) then a `temperature:` group (`C`, `F`, `K` with their names), in the format above, empty stderr, exit 0 |
| AC-8.2 | `conv --units 1 C F` and `conv --units --list`: stderr ends with one `conv: error:` line, empty stdout, no traceback, exit 1 |
| AC-8.3 | A fresh default registry with an extra `area` quantity (`a`, `ha`) passed as `main(["--units"], registry=r)` returns 0 and lists `area`, `distance`, `temperature` in that order — built from registry data, not hard-coded |

### README: adding a quantity

The README section `## Adding a quantity`, between `## Run` and `## Test`,
tells a maintainer how to add a quantity: the affine formula, the `Unit` and
`Quantity` fields with their defaults, a runnable example registering `length`
(`m`, `km`) on a fresh registry and converting `1 km → m` to `1000.0`, where
built-in quantities go (`build_default_registry()`) and how that differs from a
runtime registry, the uniqueness and cross-quantity rules, and the tests that
pin the built-in list.

Decisions:

| Decision | Why |
|---|---|
| The example builds its own registry, never touches `DEFAULT_REGISTRY` | Registering there would break AC-2.1 and AC-4.1 for the rest of a pytest process |
| `tests/unit/test_readme.py` runs the example | The only automatic guard against the example drifting from the API; it selects the block under `## Adding a quantity`, not the one under `## Run`, and fails if the heading or block is missing |
| A change that adds a built-in quantity updates AC-2.1, AC-4.1 and `tests/unit/test_registry.py` in its own spec change | Those expectations pin the default registry to temperature only |

| Id | Criterion |
|---|---|
| AC-5.1 | `README.md` has exactly one `## Adding a quantity` line, after `## Run` and before `## Test` |
| AC-5.2 | The section states `base = value * factor + offset`, that `Unit` and `Quantity` come from `conv.registry`, and every field of each with its default as defined in `conv.registry` |
| AC-5.3 | The section has exactly one `python` block; run alone with `uv run python` it exits 0 with empty stderr, imports only from `conv` and `conv.registry`, binds `registry`, registers `length` (`m` factor 1, `km` factor 1000) and shows `convert(1, "km", "m", registry=registry)` as `1000.0` |
| AC-5.4 | The section names `build_default_registry()` as the place for a built-in quantity, says `conv --list`, `conv <value> <from> <to>` and `convert()` without `registry=` pick it up, and says a runtime registry is used only where it is passed |
| AC-5.5 | The section states the case-insensitive uniqueness rule (`ValueError`, registry unchanged) and that cross-quantity conversion raises `conv.ConversionError`, a `ValueError` |
| AC-5.6 | The section states that a built-in quantity changes `conv --list` (pinned by AC-4.1) and the default registry pinned by AC-2.1 and `tests/unit/test_registry.py`, and that its spec change must update them |
| AC-5.7 | `tests/unit/test_readme.py` runs the section's block and asserts the `1000.0` result; it fails if the heading or block is missing |

AC-5.8 to AC-5.10 constrained that change only (no diff under `src`,
`tests/acceptance` or `pyproject.toml`; README lines only added; full suite
and ruff green) and passed when it merged.

## Still to check

| Criterion | Feature | What is open |
|---|---|---|
| No network access, no file writes | [CLI conversion](#cli-conversion) | A product constraint with no test and no recorded verdict; only `dependencies = []` and the 0.5 s run are tested |
| AC-5.2 | [README: adding a quantity](#readme-adding-a-quantity) | Checked by reading only. `Quantity` has since gained `min_tolerance` and `below_min_message`, which the README's field table does not list, so "every field as defined in `conv.registry`" needs a re-check |
