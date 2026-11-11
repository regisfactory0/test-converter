---
title: README section on adding a quantity
status: ready
ticket: —              # this project uses no ticket system
origin: —
created: 2026-11-11
updated: 2026-11-11
owner: ba
---

# README section on adding a quantity

## Problem

The README says new quantities "can be added without rewriting the CLI or the
library", but nothing tells a maintainer how. There is no description of the
`Unit` and `Quantity` data model, no example of registering a quantity, no
pointer to where built-in quantities live, and no warning that the existing
acceptance tests pin the default registry to temperature only. A maintainer
has to read `conv.registry` and `conv.core` to find out.

## Scope

**In scope:**
- A new `## Adding a quantity` section in `README.md` covering the data model,
  a runnable example, where built-in quantities go, the registration and
  conversion errors, and the tests that pin the built-in quantity list.
- A unit test that runs the README example, so the example cannot drift from
  the API.

**Out of scope:**
- Any change under `src/` or `tests/acceptance/`, and any change to
  `pyproject.toml`.
- Adding a real quantity (length, mass, volume) to `build_default_registry()`.
- Fixing registry validation gaps found while writing this spec (zero
  `factor`, unchecked `Quantity.base`, duplicate quantity names); they are
  recorded in `issues.md`.
- Rewording the README's other sections.

## Acceptance criteria

- AC-5.1: `README.md` contains exactly one line that is exactly
  `## Adding a quantity`. It sits after the `## Run` section and before the
  `## Test` section.
- AC-5.2: The section states the formula `base = value * factor + offset`, says
  `Unit` and `Quantity` are imported from `conv.registry`, and names every
  field of each dataclass with its default as defined in `conv.registry`:
  - `Unit`: `symbol`, `name`, `aliases` (default `()`), `factor` (default
    `1.0`), `offset` (default `0.0`).
  - `Quantity`: `name`, `base` (the base unit's symbol), `units` (ordered; the
    order is the one `conv --list` prints), `min_base` (default `None`;
    temperature uses `0.0`, absolute zero).
- AC-5.3: The section contains exactly one fenced block tagged `python`. Run
  on its own in a fresh interpreter (`uv run python` with the block as the
  program), it exits 0 with no output on stderr. The block:
  - imports only from `conv` and `conv.registry`;
  - creates a registry bound to the name `registry`, with `Registry()` or
    `build_default_registry()`;
  - calls `registry.register(Quantity(...))` with a quantity named `length`,
    base `m`, and units `m` (factor 1) and `km` (factor 1000);
  - calls `convert(1, "km", "m", registry=registry)` and shows the result as
    `1000.0`.
  After the block has run, `registry.find("km")` is not `None` and
  `convert(1, "km", "m", registry=registry) == 1000.0`.
- AC-5.4: The section names `build_default_registry()` in
  `src/conv/registry.py` as the place to add a built-in quantity. It states
  that `conv --list`, `conv <value> <from> <to>` and `convert()` called
  without `registry=` pick the quantity up with no other code change. It also
  states that a quantity registered at runtime on your own registry is used
  only where that registry is passed (`convert(..., registry=...)` or
  `conv.cli.main(argv, registry)`), not by the `conv` command.
- AC-5.5: The section states both rules:
  - symbols, names and aliases must be unique across the whole registry,
    compared case-insensitively, or `register` raises `ValueError` and leaves
    the registry unchanged;
  - converting between units of different quantities raises
    `conv.ConversionError`, a subclass of `ValueError`.
- AC-5.6: The section states that adding a built-in quantity changes the
  `conv --list` output, which AC-4.1 pins to temperature only (in
  `tests/acceptance/test_list.py`). It also states that AC-2.1 and the unit
  tests in `tests/unit/test_registry.py` pin the default registry to
  temperature only. It states that a change request adding a built-in quantity
  must update those expectations as part of its spec change.
- AC-5.7: `tests/unit/test_readme.py` exists. It finds the `python` block under
  `## Adding a quantity` (not the block under `## Run`), runs it, and asserts
  `convert(1, "km", "m", registry=<the block's registry>) == 1000.0`. It fails
  if the heading or the block is missing. It passes against the new README.
- AC-5.8: `git diff main -- src tests/acceptance pyproject.toml` is empty.
- AC-5.9: `git diff main -- README.md` contains only added lines: no line
  outside the new section is removed or changed.
- AC-5.10: `uv run pytest` passes, including every test for AC-1.1 to AC-4.3.
  `uv run ruff check .` and `uv run ruff format --check .` both exit 0.

None of these criteria is manual. AC-5.2 and AC-5.4 to AC-5.6 are checked by
reading the section against the listed facts.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| `README.md` | yes | New section only |
| Library (`conv.registry`, `conv.core`) | no | Documented as it is; not changed |
| CLI (`conv.cli`) | no | Documented as it is; not changed |
| Unit tests (`tests/unit/`) | yes | One new file, `test_readme.py` |
| Acceptance tests (`tests/acceptance/`) | no | Not touched, per the request |

Verified against the code:
- `Unit` and `Quantity` are frozen dataclasses with the fields and defaults
  listed in AC-5.2.
- `Registry()` takes no arguments. `Registry.register(quantity)` raises
  `ValueError` on any case-insensitive symbol, name or alias clash, and
  changes nothing when it does.
- `build_default_registry()` returns a fresh registry holding temperature.
- `DEFAULT_REGISTRY` is built from `build_default_registry()` at import time.
  `convert()` without `registry=` and `conv.cli.main` with `registry=None`
  both use it, so a built-in quantity reaches the CLI with no other change.
- `convert(value, from_unit, to_unit, registry=None)` raises
  `ConversionError` for cross-quantity units, with the message
  `units are of different quantities: 'm' is length, 'C' is temperature`.
- The example in AC-5.3 was run on this branch. Both `Registry()` and
  `build_default_registry()` give exactly `1000.0`.

## Design

Add one Markdown section to `README.md` between `## Run` and `## Test`, in
this order:

1. **Model.** One paragraph with the affine formula, then a table each for the
   `Unit` and `Quantity` fields (AC-5.2).
2. **Example.** One `python` block that registers `length` on a fresh registry
   and converts `1 km` to `m`. Show the result with a trailing `# 1000.0`
   comment, the style already used in `## Run` (AC-5.3).
3. **Built-in quantities.** Where they go, what picks them up, and how that
   differs from a runtime registry (AC-5.4).
4. **Rules.** Uniqueness and cross-quantity errors (AC-5.5).
5. **Changing the built-in list.** The pinned expectations and the need to
   update them in the spec change (AC-5.6).

`tests/unit/test_readme.py` reads `README.md` from the repository root,
relative to the test file. It slices the text from the `## Adding a quantity`
heading to the next `## ` heading, takes the single `python` fenced block in
that slice, and `exec`s it in a fresh namespace. It then asserts on
`namespace["registry"]`. It uses only the standard library and keeps to
`.claude/rules/code-style.md`: plain pytest functions, type hints, no
comments.

## Affected modules and layers

- Modules: `README.md`; `tests/unit/test_readme.py` (new). No source module
  changes.
- Layers: none. The documentation describes the `registry` and `core` layers
  as they are.
- Key types: `conv.registry.Unit`, `conv.registry.Quantity`,
  `conv.registry.Registry`, `conv.registry.build_default_registry`,
  `conv.convert`, `conv.ConversionError` (documented, not changed).

## UI

n/a. No CLI output or option changes; the README is documentation.

- Screens / entry points: n/a, no entry point added or changed.
- New reusable components: n/a.
- Design link: n/a.

## Data

- Schema or persisted-shape changes: no.
- New or changed repositories, APIs, caches: none. The registry API is
  documented, not changed.

## Edge cases

- The example must not touch `DEFAULT_REGISTRY`. Registering `length` there
  would break AC-2.1 and AC-4.1 for the rest of a pytest process, so the
  example works on a registry it creates itself (AC-5.3).
- With `build_default_registry()`, the new `m` and `km` must not clash with
  `C`, `F`, `K` or their names. Verified: they do not.
- The README already has a `python` block under `## Run`. The test must
  select the one under the new heading (AC-5.7).
- If the heading is renamed or the block is removed, the test fails rather
  than passing on nothing (AC-5.7).
- A reader who registers a quantity at runtime and expects the `conv` command
  to see it: covered by the runtime-versus-built-in statement (AC-5.4).
- `factor=0` passes `register` but makes `convert` raise
  `ZeroDivisionError`, not `ConversionError`. The CLI does not catch that, so
  it would print a traceback. This is a code gap, not documentation, so it is
  out of scope and recorded in `issues.md`. The README does not have to
  mention it.
- Integer factors (`factor=1000`) give the same `1000.0` as `1000.0`.
  Verified.

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| The README example drifts from the API in a later change | medium | AC-5.7 runs the example in the unit suite |
| The section misstates a default or a rule | low | AC-5.2 and AC-5.5 list the exact facts verified against `conv.registry` and `conv.core` |
| The edit changes other README text by accident | low | AC-5.9 allows only added lines |
| The test runs the example against `DEFAULT_REGISTRY` and leaks state into other tests | low | The example builds its own registry (AC-5.3); the test asserts on that registry only |

- Rollback: revert the change. Nothing is persisted and no code depends on it.

## Test plan

- Unit / integration: `tests/unit/test_readme.py` (AC-5.7), run with
  `uv run pytest tests/unit/test_readme.py`. The full `uv run pytest` and both
  ruff commands cover AC-5.10.
- End-to-end / UI: none new. The existing acceptance suite in
  `tests/acceptance/` must stay green unchanged (AC-5.8, AC-5.10). QA checks
  AC-5.1 to AC-5.6 by reading the section against the listed facts. QA runs
  the extracted block with `uv run python` for AC-5.3, and runs the two
  `git diff` commands for AC-5.8 and AC-5.9.

## Open questions

- AC-5.6 also names AC-2.1 and `tests/unit/test_registry.py`. The request
  named only AC-4.1, but `test_default_registry_holds_temperature` (AC-2.1)
  and unit tests in `tests/unit/test_registry.py` also assert that the default registry is temperature
  only. Naming only AC-4.1 would leave the README incomplete. Assumed in; drop
  it if the user wants AC-4.1 alone.
- The README does not have to cite AC-2.3 and AC-2.4 by id. The request put
  them in parentheses, which reads as traceability for this spec. Assumed:
  the README may cite them but is not required to.
- The README example test is in scope (AC-5.7). The request made it optional;
  it is included because it is the only automatic guard against the example
  drifting. Drop AC-5.7 if the user does not want it.

## Links

- Ticket: —
- Design: n/a
- Related specs: `specs/features/archive/temperature-library/spec.md`
  (AC-2.1 to AC-2.4, registry model), `specs/features/archive/list-units/spec.md`
  (AC-4.1), `specs/features/archive/cli-conversion/spec.md`
