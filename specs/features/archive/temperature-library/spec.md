---
title: Temperature conversion library and unit registry
status: done
ticket: —              # this project uses no ticket system
origin: —
created: 2026-11-10
updated: 2026-11-10
owner: developer
---

# Temperature conversion library and unit registry

## Problem

There is no library function to convert values between units. Two kinds of
users need it:

- **Library user** — *As a library user, I want to call
  `conv.convert(value, from_unit, to_unit)`, so that my code can convert
  temperatures without shelling out to the CLI.*
- **Maintainer** — *As a maintainer, I want units defined as data grouped by
  quantity, so that adding a quantity later means adding registry entries, not
  new code branches.*

Both are `must`. Together they form the core every other feature builds on:
the CLI calls `convert`, and `--list` reads the registry.

## Scope

**In scope:**
- `conv.convert(value, from_unit, to_unit, registry=None) -> float` and
  `conv.ConversionError` (a subclass of `ValueError`), re-exported from
  `conv/__init__.py`.
- Temperature conversion between C, F and K in all six directions, plus
  same-unit identity.
- The `Unit`, `Quantity` and `Registry` data types in `conv/registry.py`, a
  default registry holding exactly `temperature`, and a way to build a fresh
  registry for tests.
- Rejecting unknown units, values below absolute zero, non-finite values,
  overflow to infinity, cross-quantity conversion, and duplicate unit
  spellings at registration.

**Out of scope:**
- The command line (its own feature) and `conv --list` (its own feature).
- Rounding: `convert` returns the full-precision float; only the CLI rounds.
- Quantities other than temperature in the default registry (length, mass,
  volume…); tests register dummy quantities on their own registry instances.
- Other temperature scales (Rankine, Réaumur, …).
- Degree-sign spellings (`°C`), plurals (`kelvins`), `degC` and similar.

## Acceptance criteria

Library conversion function:

- AC-1.1: Given the library, when I call `convert(100, "C", "F")`, then it returns `212.0`.
- AC-1.2: Given the library, when I call `convert` for each of the six directions with known pairs (0 °C = 32 °F = 273.15 K; 100 °C = 212 °F = 373.15 K; −40 °C = −40 °F), then each result equals the expected value within an absolute tolerance of 1e-9.
- AC-1.3: Given the library, when I call `convert(37.5, "K", "K")` (same unit), then it returns `37.5`.
- AC-1.4: Given unit names in any letter case (`"c"`, `"C"`) or as full names (`"celsius"`, `"Fahrenheit"`, `"kelvin"`), when I call `convert`, then they resolve to the same units as the symbols.
- AC-1.5: Given an unknown unit such as `"X"`, an empty string, a degree-sign spelling (`"°C"`) or a plural (`"kelvins"`, `"degrees"`), when I call `convert`, then it raises `ConversionError` (a subclass of `ValueError`) whose message names the unknown unit.
- AC-1.6: Given a value below absolute zero (e.g. `convert(-300, "C", "K")` or `convert(-1, "K", "C")`), when I call `convert`, then it raises `ConversionError` with a message mentioning absolute zero.
- AC-1.7: Given a non-finite value (`float("nan")`, `float("inf")`), when I call `convert`, then it raises `ConversionError`.
- AC-1.8: Given a value exactly at absolute zero in any unit (`convert(0, "K", "C")`, `convert(-273.15, "C", "K")`, `convert(-459.67, "F", "K")`), when I call `convert`, then no error is raised and the result equals the expected value (`-273.15`, `0.0`, `0.0`) within an absolute tolerance of 1e-9.
- AC-1.9: Given a very large finite value (`1e300` C → F), when I call `convert`, then it returns a finite float or raises `ConversionError` if the result overflows to infinity — never returns `inf`.

Unit registry per quantity:

- AC-2.1: Given the registry, when I list its quantities, then it contains exactly `temperature`, with units `C`, `F`, `K` (each with its symbol, full name and aliases).
- AC-2.2: Given a test that registers a new quantity with two units (e.g. a dummy `length` with `m` and `km`, factor 1000) on a fresh registry, when I convert `1 km` to `m` through the same conversion code, then it returns `1000.0` — without changing any library or CLI code.
- AC-2.3: Given two units from different quantities in a registry (the test's dummy `m` and `C`), when I convert between them, then `ConversionError` is raised with a message saying the units are of different quantities.
- AC-2.4: Given an attempt to register a unit whose symbol or alias already exists (case-insensitive), when it is registered, then a `ValueError` is raised.

None of these criteria is manual.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| Python library (`import conv`) | yes | the public API this feature delivers |
| CLI (`conv`) | no | built on this feature by the CLI feature |
| Linux, Python 3.12 | yes | the only supported platform |

## Design

`conv/registry.py` holds the data; `conv/core.py` holds the logic. The
dependency direction is `core` → `registry`; neither imports the CLI.

**Data types** (already stubbed in `src/conv/registry.py`; keep the names and
fields, the acceptance tests construct them with keyword arguments):

- `Unit(symbol: str, name: str, aliases: tuple[str, ...] = (), factor: float = 1.0, offset: float = 0.0)`
  — affine to its quantity's base unit: `base = value * factor + offset`.
- `Quantity(name: str, base: str, units: tuple[Unit, ...], min_base: float | None = None)`
  — `base` is the base unit's symbol; `units` keep their order; `min_base` is
  the lowest allowed base value (temperature: `0.0`).
- `Registry()` — starts empty. `register(quantity)` adds a quantity and its
  units; `quantities()` returns the quantities in registration order. It
  looks units up case-insensitively by symbol, name or alias.
- `build_default_registry()` returns a fresh registry holding `temperature`;
  `DEFAULT_REGISTRY` is the module-level instance built from it at import time
  and only read afterwards.

**Temperature** (base kelvin, `min_base = 0.0`), units in this order:

| Symbol | Name | Factor | Offset |
|---|---|---|---|
| `C` | `celsius` | 1 | 273.15 |
| `F` | `fahrenheit` | 5/9 | 459.67 · 5/9 |
| `K` | `kelvin` | 1 | 0 |

Aliases are empty: the accepted spellings are exactly the symbols `C`, `F`,
`K` and the names `celsius`, `fahrenheit`, `kelvin`, case-insensitive.

**Registration.** Every lookup key of a unit (its symbol, name and aliases,
compared case-insensitively) must be unique across the whole registry,
including the other units of the same quantity; a clash raises `ValueError`
and leaves the registry unchanged. (Names are lookup keys too, so a clash with
a name is rejected for the same reason.)

**`convert(value, from_unit, to_unit, registry=None)`** — `None` means
`DEFAULT_REGISTRY`:

1. Reject a non-finite `value` (`ConversionError`).
2. Look up both units; an unknown spelling (including `""`) raises
   `ConversionError` whose message contains the spelling as given.
3. If the units belong to different quantities, raise `ConversionError`
   saying the units are of different quantities.
4. `base = value * factor + offset`. If the quantity has a `min_base` and
   `base < min_base - 1e-9`, raise `ConversionError` mentioning
   "absolute zero" for temperature (for other quantities, wording of the
   developer's choice). A base within the tolerance below `min_base` is
   clamped to `min_base`.
5. Convert from base to the target: `(base - offset) / factor`. If the result
   is not finite (overflow), raise `ConversionError`.
6. Return the result as a `float` (an `int` input returns a float).

`ConversionError` subclasses `ValueError`. Error wording is the developer's
choice beyond naming the offending unit and mentioning absolute zero.

## Affected modules and layers

- Modules: `src/conv/registry.py`, `src/conv/core.py`, `src/conv/__init__.py`
- Layers: `core`, `registry`
- Key types: `Unit`, `Quantity`, `Registry`, `ConversionError`, `convert`

## UI

n/a — library only; no user interface.

- Screens / entry points: `conv.convert`
- New reusable components: n/a
- Design link: n/a

## Data

- Schema or persisted-shape changes: no — the registry is in-code data.
- New or changed repositories, APIs, caches: the public API `conv.convert`,
  `conv.ConversionError`; `conv.registry` types.

## Edge cases

- Empty unit string → AC-1.5.
- Unknown unit, degree sign, plurals → AC-1.5.
- Boundary at absolute zero, including float rounding at the boundary →
  AC-1.6, AC-1.8 (1e-9 K tolerance, clamp to the boundary).
- Maximum input / overflow → AC-1.9.
- NaN / inf → AC-1.7.
- Integer input → AC-1.1 (int accepted, float returned).
- Cross-quantity conversion → AC-2.3.
- Duplicate symbols / aliases → AC-2.4.
- Empty registry / unknown quantity → covered by AC-1.5 (unknown unit).
- Concurrent use: `convert` is a pure function; the registry is built at
  import time and only read afterwards. Nothing to test.
- Offline / missing service: no external services.

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| Registry design too temperature-specific (offsets) for later quantities | low | affine factor + offset covers linear units too (offset 0); AC-2.2 proves it with a dummy quantity |
| Float rounding rejects exactly 0 K (`-459.67 F`) | medium | 1e-9 K tolerance and clamping; AC-1.8 |

- Rollback: revert the feature's commits; nothing is persisted.

## Test plan

- Unit / integration: unit tests in `tests/unit/` for registration and lookup
  details (clash rules, ordering, clamping).
- End-to-end / UI: acceptance tests in `tests/acceptance/test_library.py`,
  run with `uv run pytest tests/acceptance/test_library.py`.

## Open questions

- None.

## Verification

QA verdicts, 2026-11-10. `tests/acceptance/test_library.py` and `tests/unit`
pass; failures elsewhere in the suite belong to the CLI and list features.

| Criterion | Verdict | Note |
|---|---|---|
| AC-1.1 | pass | `convert(100, "C", "F")` returns `211.99999999999997`, within 1e-9 of `212.0`; not bit-exact |
| AC-1.2 | pass | |
| AC-1.3 | pass | |
| AC-1.4 | pass | |
| AC-1.5 | pass | |
| AC-1.6 | pass | |
| AC-1.7 | pass | |
| AC-1.8 | pass | |
| AC-1.9 | pass | |
| AC-2.1 | pass | |
| AC-2.2 | pass | |
| AC-2.3 | pass | |
| AC-2.4 | pass | |

AC-1.1 observation: the criterion reads "returns `212.0`", but the float result
is `211.99999999999997`. AC-1.2 sets the 1e-9 tolerance, and the CLI rounds to
6 places, so `conv 100 C F` prints `212.0`.

## Links

- Ticket: —
- Design: n/a
- Related specs: `specs/features/backlog/cli-conversion/spec.md`,
  `specs/features/backlog/list-units/spec.md`
