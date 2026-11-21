---
title: List supported units
status: ready
ticket: —              # this project uses no ticket system
origin: —
created: 2026-11-21
updated: 2026-11-21
owner: developer
---

# List supported units

## Problem

A CLI user can see the units of one registry at a time (`conv --list` for
temperature, `conv -d --list` for distance), each quantity on one long line.
There is no single command that shows every unit the tool supports.
*As a CLI user, I want `conv --units` to list every supported unit, one per
line, grouped by quantity, so that I can see at a glance what I can convert,
with or without `--distance`.*
Priority: `should`.

## Scope

**In scope:**
- A CLI flag `--units` in `src/conv/cli.py` that prints the units of the
  default registry and the distance registry together: one `<quantity>:`
  header line per quantity, then one line per unit, `  <symbol> (<name>)`
  (indented two spaces); quantities in alphabetical order of name, units in
  registration order; exit code 0.
- `-d` / `--distance` may be combined with `--units`; the output is the same
  full list.
- `--help` may mention `--units`.

**Out of scope:**
- A mass quantity or any new unit; renaming `distance` to `length` (the
  `distance` quantity is listed under its existing name).
- Any change to `conv --list` or `conv -d --list` output (AC-4.1, AC-7.7).
- Listing aliases (e.g. US spellings such as `meter`).
- A new module or dependency; a subcommand `conv units`.

## Acceptance criteria

- AC-8.1: Given the installed CLI, when I run `conv --units` or `conv -d --units`, then stdout is exactly the following 13 lines, each followed by a newline, stderr is empty and the exit code is 0:
  ```
  distance:
    mm (millimetre)
    cm (centimetre)
    m (metre)
    km (kilometre)
    in (inch)
    ft (foot)
    yd (yard)
    mi (mile)
  temperature:
    C (celsius)
    F (fahrenheit)
    K (kelvin)
  ```
- AC-8.2: Given `--units` combined with other arguments (`conv --units 1 C F`, `conv --units --list`), when I run it, then stderr ends with one line starting with `conv: error:` (a short usage line may come before it), stdout is empty, no traceback is printed and the exit code is 1.
- AC-8.3: Given a fresh default registry with an extra quantity `area` (units `a`, `ha`) registered and passed to `conv.cli.main(["--units"], registry=r)`, when it runs, then it returns 0 and the output lists the groups `area`, `distance`, `temperature` in that order, each group's units in registration order, in the format of AC-8.1 — the list is built from registry data, not hard-coded.

None of these criteria is manual.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| CLI (`conv --units`, `conv -d --units`) | yes | the deliverable |
| CLI conversion, `--list`, `-d --list`, `--help` | yes | must stay exactly as before (AC-3.x, AC-4.x, AC-7.x) |
| Python library (`conv.convert`, registries) | no | read through `Registry.quantities()`, not changed |
| Linux, Python 3.12 | yes | the only supported platform |

## Design

In `src/conv/cli.py`, `main` handles `--units` next to `--list`: after the
`-d` / `--distance` flags are taken out of the argument list, `--units` must
be the only argument left; otherwise print the usage line and one
`conv: error:` line to stderr and return 1 (this also covers
`--units --list` in either order). With `--units` alone, `main` gathers the
quantities of the registry for runs without the flag (`registry`, default
`DEFAULT_REGISTRY`) and of the distance registry (`distance_registry`,
default `DISTANCE_REGISTRY`), sorts them by name and prints, for each,
`<name>:` and then `  <symbol> (<name>)` for each unit in registration
order. Return 0.

Because `-d` swaps `registry` for the distance registry today, the `--units`
branch must take both registries regardless of the flag, so that
`conv -d --units` prints the same full list. A quantity name appearing in both
registries is not reachable in the product; how the merge treats it is the
developer's choice. Update `USAGE` / `HELP` to mention `--units` if wished
(AC-3.9 and AC-7.8 must still hold).

## Affected modules and layers

- Modules: `src/conv/cli.py`
- Layers: `cli` (reads `registry`)
- Key types: `main`, `USAGE`, `HELP`, `Registry.quantities()`, `Quantity`, `Unit`

## UI

- Screens / entry points: `conv --units`, `conv -d --units`,
  `conv.cli.main(["--units"], registry=r)`.
- New reusable components: n/a
- Design link: n/a

## Data

- Schema or persisted-shape changes: no
- New or changed repositories, APIs, caches: none; `main` keeps its signature.

## Edge cases

- Combined with `-d` / `--distance` → AC-8.1 (same full list).
- Combined with conversion arguments or `--list` → AC-8.2.
- Order of groups and units → AC-8.1, AC-8.3 (alphabetical by quantity name,
  units in registration order).
- New quantities added later → AC-8.3 (built from registry data).
- The request's "mass" group → not in the product, no units to list.
- The request's "length" → the product's `distance` quantity, listed under
  its existing name.
- Empty registry → not reachable (temperature and distance are always
  registered), no test needed.
- `conv --list` and `conv -d --list` unchanged → AC-4.1 and AC-7.7 keep passing.
- Offline / permissions: the tool touches no files or network.

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| `--units` parsing breaks the existing argument handling (`--list`, `-d`, negative values) | low | the whole earlier acceptance suite keeps running; AC-8.2 covers the combinations |
| `-d --units` lists only distance | medium | AC-8.1 tests `conv -d --units` explicitly |

- Rollback: revert the feature's commits; nothing is persisted.

## Test plan

- Unit / integration: unit tests in `tests/unit/` for the `--units` branch of
  `main` with fresh in-memory registries.
- End-to-end / UI: acceptance tests in `tests/acceptance/test_units.py`
  (subprocess runs of the installed `conv`, and `main` with a test registry);
  `uv run pytest tests/acceptance/test_units.py`.

## Open questions

- None.

## Links

- Ticket: —
- Design: n/a
- Related specs: `specs/features/archive/list-units/spec.md`,
  `specs/features/archive/cli-distance/spec.md`.
