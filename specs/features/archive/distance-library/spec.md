---
title: Distance registry and library conversion
status: done
ticket: —              # this project uses no ticket system
origin: —
created: 2026-11-15
updated: 2026-11-15
owner: developer
---

# Distance registry and library conversion

## Problem

The library converts only temperatures. A library user cannot convert
between metric (mm, cm, m, km) and imperial (in, ft, yd, mi) distances.
*As a library user, I want a distance registry I can pass to `conv.convert`,
so that my code can convert between metric and imperial distances with the
same function it uses for temperature.*
Priority: `must`.

## Scope

**In scope:**
- A public function `conv.registry.build_distance_registry()` returning a
  fresh `Registry` holding only the `distance` quantity (base `m`), with the
  units mm, cm, m, km, in, ft, yd, mi in that order.
- Exact international factors to metres (1959 yard and pound agreement).
- Rejecting negative distances in `convert` with a `ConversionError` whose
  message contains `negative`; zero and `-0.0` are allowed.
- Optionally a module-level `DISTANCE_REGISTRY` next to `DEFAULT_REGISTRY`.

**Out of scope:**
- Distance in the default registry (`build_default_registry()` and
  `DEFAULT_REGISTRY` keep exactly `temperature`).
- The CLI flag `-d` / `--distance` (feature `cli-distance`).
- Other distance units (nautical mile, µm, light-year, survey foot, …),
  plural spellings (`feet`, `miles`, `inches`), compound input (`5 ft 3 in`).
- Other quantities (mass, volume, …).

## Acceptance criteria

- AC-6.1: Given the library, when I call `conv.registry.build_distance_registry()`, then it returns a fresh registry with exactly one quantity, `distance`, whose base unit is `m` and whose units are, in this order, `mm` (millimetre), `cm` (centimetre), `m` (metre), `km` (kilometre), `in` (inch), `ft` (foot), `yd` (yard), `mi` (mile).
- AC-6.2: Given the distance registry `r`, when I call `convert(1, from, to, registry=r)` for these pairs, then each result matches within `rel_tol=1e-12, abs_tol=1e-9`: `mi→km` 1.609344, `ft→in` 12, `yd→m` 0.9144, `in→mm` 25.4, `in→cm` 2.54, `km→m` 1000, `m→cm` 100, `mi→ft` 5280, `mi→yd` 1760, `ft→m` 0.3048.
- AC-6.3: Given the distance registry, when I convert `x = 123.456` from each of the 8 units to each of the 8 units and back again (all 64 ordered pairs, same-unit pairs included), then each round trip returns `x` within `rel_tol=1e-12`.
- AC-6.4: Given unit spellings in any letter case — the symbols (`MI`, `Km`), the names (`mile`, `Metre`, `inch`, `foot`, `yard`, `millimetre`, `centimetre`, `kilometre`) and the US spellings (`meter`, `millimeter`, `centimeter`, `Kilometer`) — when I call `convert` with the distance registry, then they resolve to the same units as the symbols.
- AC-6.5: Given a spelling that is not a distance unit — a plural (`feet`, `miles`, `inches`, `meters`), an empty string, an unsupported unit (`nmi`) or a temperature unit (`C`) — when I call `convert` with the distance registry, then it raises `ConversionError` whose message names that spelling.
- AC-6.6: Given a negative value (`convert(-1, "mi", "km", registry=r)`, `convert(-0.5, "m", "ft", registry=r)`, `convert(-1e-6, "mm", "m", registry=r)`), when I call `convert`, then it raises `ConversionError` whose message contains the word `negative`; and given zero (`convert(0, "ft", "m", registry=r)`, `convert(-0.0, "km", "mi", registry=r)`), no error is raised and it returns `0.0`.
- AC-6.7: Given a non-finite value (`nan`, `inf`) or a finite value whose result overflows (`convert(1e308, "mi", "mm", registry=r)`), when I call `convert` with the distance registry, then it raises `ConversionError` and never returns `inf` or `nan`.
- AC-6.8: Given the default registry (no `registry` argument), when I call `convert(1, "mi", "km")`, then it raises `ConversionError` naming `mi`, and `build_default_registry()` still contains exactly `temperature`.

None of these criteria is manual.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| Python library (`conv.registry`, `conv.convert`) | yes | the deliverable |
| CLI | no | distance mode comes with `cli-distance`; plain `conv` is unchanged |
| Linux, Python 3.12 | yes | the only supported platform |

## Design

In `src/conv/registry.py`, add `build_distance_registry()` next to
`build_default_registry()`. It registers one `Quantity(name="distance",
base="m", units=…)` whose units are linear (offset 0) with these factors to
metres:

| Symbol | Name | Aliases | Factor |
|---|---|---|---|
| `mm` | millimetre | `millimeter` | 0.001 |
| `cm` | centimetre | `centimeter` | 0.01 |
| `m` | metre | `meter` | 1 |
| `km` | kilometre | `kilometer` | 1000 |
| `in` | inch | — | 0.0254 |
| `ft` | foot | — | 0.3048 |
| `yd` | yard | — | 0.9144 |
| `mi` | mile | — | 1609.344 |

Each unit's `name` is the UK spelling; the US spellings are aliases;
imperial units have no aliases. Lookup is already case-insensitive
(`Registry.find`), so letter case needs no new code.

Negative distances: every value below 0 is rejected, with no boundary
tolerance; `-0.0` counts as zero. How the registry expresses this is the
developer's choice — for example `min_base=0.0` on the distance quantity plus
a per-quantity tolerance and error message (`Quantity` gets optional fields,
or the core keeps a small per-quantity table). Whatever the shape, the
temperature quantity must keep its "absolute zero" message and its 1e-9 K
tolerance and clamp (AC-1.6, AC-1.8), and every existing test keeps passing.

`convert` already rejects non-finite input and overflowing results and
already raises `ConversionError` naming an unknown spelling; the distance
registry gets these for free (AC-6.5, AC-6.7).

The default registry is not touched (AC-6.8). A module-level
`DISTANCE_REGISTRY = build_distance_registry()` is allowed for the CLI to use.

## Affected modules and layers

- Modules: `src/conv/registry.py`; `src/conv/core.py` only if the minimum
  check needs a per-quantity message or tolerance.
- Layers: `registry` (data), `core` (minimum check).
- Key types: `Quantity`, `Unit`, `Registry`, `build_distance_registry`,
  `convert`, `ConversionError`.

## UI

n/a — library only; the CLI part is the `cli-distance` feature.

- Screens / entry points: `conv.registry.build_distance_registry()`,
  `conv.convert(value, from_unit, to_unit, registry=r)`.
- New reusable components: n/a
- Design link: n/a

## Data

- Schema or persisted-shape changes: no (in-code data only)
- New or changed repositories, APIs, caches: new public function
  `conv.registry.build_distance_registry()`; possibly new optional fields on
  `Quantity` (with defaults, so existing calls keep working).

## Edge cases

- Plurals, empty string, unsupported and temperature units → AC-6.5.
- Letter case and US/UK spelling → AC-6.4.
- Negative values, including tiny ones like `-1e-6`, and zero / `-0.0` → AC-6.6.
- Temperature's absolute-zero rule unaffected → AC-1.6/AC-1.8 keep passing.
- NaN/inf and overflow → AC-6.7.
- Float noise in exact factors → tolerances in AC-6.2/AC-6.3.
- Same-unit conversion → AC-6.3.
- Distance leaking into the default registry → AC-6.8.
- Alias clashes inside the distance quantity → `Registry.register` raises at
  build time, so AC-6.1 passing proves there are none.
- Concurrent use: registry built once and only read, nothing to test.
- Offline / missing service: no external services.

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| Making the minimum-value check generic breaks temperature's "absolute zero" message or its 1e-9 K tolerance | low | AC-1.6/AC-1.8 stay in the suite; keep temperature's behaviour as is |
| Users pass plurals (`feet`) | medium | rejected with a clear error naming the spelling (AC-6.5); aliases can be added later as data |

- Rollback: revert the feature's commits; nothing is persisted.

## Test plan

- Unit / integration: unit tests in `tests/unit/` for the distance quantity's
  data and the negative-value check (and that temperature's message is
  unchanged).
- End-to-end / UI: acceptance tests in
  `tests/acceptance/test_distance_library.py`;
  `uv run pytest tests/acceptance/test_distance_library.py`.

## Open questions

- None.

## Links

- Ticket: —
- Design: n/a
- Related specs: `specs/features/archive/temperature-library/spec.md` (the
  registry and `convert` this builds on); `specs/features/archive/cli-distance/spec.md`
  (built after this one).
