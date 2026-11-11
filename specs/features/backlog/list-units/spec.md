---
title: List quantities and units
status: ready
ticket: —              # this project uses no ticket system
origin: —
created: 2026-11-10
updated: 2026-11-10
owner: developer
---

# List quantities and units

## Problem

A CLI user cannot see which units `conv` knows without reading the code.
*As a CLI user, I want `conv --list` to show the known quantities and their
units, so that I know what I can convert without reading the code.*
Priority: `should`.

## Scope

**In scope:**
- A `--list` option in `conv.cli.main` that prints every quantity of the
  registry passed to `main` (default: the library's default registry) and
  exits 0.
- Rejecting `--list` combined with conversion arguments.

**Out of scope:**
- Showing aliases, factors or offsets.
- Filtering by quantity, machine-readable output formats.
- New quantities in the default registry.

## Acceptance criteria

- AC-4.1: Given the CLI, when I run `conv --list`, then stdout is exactly:
  ```
  temperature: C (celsius), F (fahrenheit), K (kelvin)
  ```
  followed by a newline, and the exit code is 0.
- AC-4.2: Given a registry with an extra quantity registered (test double registry passed to `main`), when `--list` runs, then each quantity is printed on its own line in alphabetical order of quantity name, units in registration order.
- AC-4.3: Given `conv --list` combined with conversion arguments (`conv --list 1 C F`), when I run it, then stderr has a `conv: error:` line and the exit code is 1.

None of these criteria is manual.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| CLI (`conv --list`) | yes | the deliverable |
| Python library | no | read through `Registry.quantities()`, not changed |
| Linux, Python 3.12 | yes | the only supported platform |

## Design

In `src/conv/cli.py`, add `--list` to the existing parser. With `--list` and
no other arguments, `main` prints one line per quantity of `registry` (the
library's default when `None`), sorted by quantity name, and returns 0. Each
line is

```
<quantity name>: <symbol> (<name>), <symbol> (<name>), …
```

with the units in their registration order (`Quantity.units`). With
`--list` plus any conversion argument, in either order, `main` prints the
usual `conv: error:` line (a usage line before it is fine) and returns 1, no
traceback.

The CLI reads the registry only through `Registry.quantities()` and the
`Quantity` / `Unit` fields; it adds no conversion logic.

## Affected modules and layers

- Modules: `src/conv/cli.py`
- Layers: `cli` (reads `registry`)
- Key types: `main`, `Registry.quantities()`

## UI

- Screens / entry points: `conv --list`; `conv.cli.main(["--list"], registry=…)`.
- New reusable components: n/a
- Design link: n/a

## Data

- Schema or persisted-shape changes: no
- New or changed repositories, APIs, caches: none

## Edge cases

- Extra arguments → AC-4.3.
- Multiple quantities → AC-4.2.
- Empty registry → not reachable in the product (temperature is always
  registered), no test needed.

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| `--list` breaks the conversion arguments' parsing (e.g. negative values) | low | the conversion acceptance tests keep running |

- Rollback: revert the feature's commits; nothing is persisted.

## Test plan

- Unit / integration: unit tests in `tests/unit/` for the line format.
- End-to-end / UI: acceptance tests in `tests/acceptance/test_list.py`
  (subprocess for `conv --list`, `main(["--list"], registry=…)` with a fresh
  registry holding extra dummy quantities);
  `uv run pytest tests/acceptance/test_list.py`.

## Open questions

- None.

## Links

- Ticket: —
- Design: n/a
- Related specs: `specs/features/backlog/cli-conversion/spec.md` (built before
  this one), `specs/features/archive/temperature-library/spec.md`
