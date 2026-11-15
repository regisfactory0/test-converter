---
title: CLI distance mode
status: ready
ticket: —              # this project uses no ticket system
origin: —
created: 2026-11-15
updated: 2026-11-15
owner: developer
---

# CLI distance mode

## Problem

The CLI converts only temperatures. A CLI user cannot convert between metric
and imperial distances in one command.
*As a CLI user, I want `conv --distance <value> <from> <to>` to print the
converted distance, so that I can convert between metric and imperial units
in one command.*
Priority: `must`.

## Scope

**In scope:**
- A flag `-d` / `--distance`, accepted anywhere on the command line, that
  makes `conv.cli.main` use the distance registry
  (`conv.registry.build_distance_registry()`, from feature
  `distance-library`) for both conversion and `--list`.
- `--help` text mentioning `--distance`.
- A README section `## Distance` showing `conv --distance` usage,
  `conv -d --list` and the library call with `build_distance_registry()`;
  the `## Adding a quantity` section stays.

**Out of scope:**
- Any change to plain `conv …` and `conv --list` (no flag): they behave
  exactly as before (AC-3.x, AC-4.x).
- Distance in the default registry.
- New distance units, plurals, compound input (`5 ft 3 in`).
- Other quantities or flags.

## Acceptance criteria

- AC-7.1: Given the installed CLI, when I run `conv --distance 1 mi km` or `conv -d 1 mi km`, then stdout is exactly `1.609344\n`, stderr is empty and the exit code is 0.
- AC-7.2: Given the CLI, when I run `conv -d 100 km mi`, `conv -d 1 m ft`, `conv -d 5280 ft mi`, `conv -d 1 ft in` and `conv -d 1 yd cm`, then stdout is `62.137119\n`, `3.28084\n`, `1.0\n`, `12.0\n` and `91.44\n` respectively (same rounding and format rules as F-3), with exit code 0.
- AC-7.3: Given the CLI, when I run `conv -d -3 ft m` (negative value after the flag), then the value is read as a number, not an option: stderr has a single line starting with `conv: error:` containing the word `negative`, stdout is empty, no traceback is printed and the exit code is 1; and `conv -d 0 ft m` prints `0.0\n` with exit code 0.
- AC-7.4: Given the CLI, when I run `conv 1 mi km --distance` (flag after the positional arguments), then stdout is `1.609344\n` and the exit code is 0.
- AC-7.5: Given invalid distance input — an invalid number (`conv -d abc m ft`, `conv -d nan m ft`), a unit that is not a distance unit (`conv -d 1 C F`, naming `C`), or an overflowing value (`conv -d 1e308 mi mm`) — when I run it, then stderr has a single line starting with `conv: error:`, stdout is empty, no traceback is printed and the exit code is 1.
- AC-7.6: Given the wrong number of positional arguments with the flag (`conv -d`, `conv -d 1 m`, `conv -d 1 m ft in`), when I run it, then stderr shows a short usage line plus a `conv: error:` line and the exit code is 1.
- AC-7.7: Given `conv --distance --list` (or `conv -d --list`), when I run it, then stdout is exactly `distance: mm (millimetre), cm (centimetre), m (metre), km (kilometre), in (inch), ft (foot), yd (yard), mi (mile)` followed by a newline, and the exit code is 0; and `conv -d --list 1 m ft` writes a `conv: error:` line to stderr and exits 1.
- AC-7.8: Given `conv --help`, when I run it, then the usage text on stdout mentions `--distance` and the exit code is 0.
- AC-7.9: Given the CLI module, when I call `conv.cli.main(["--distance", "1", "mi", "km"])` with the library's `convert` patched, then `convert` is called once with a registry whose only quantity is `distance`, and `main` returns 0 — the CLI holds no distance conversion logic.
- AC-D.1: Given the README, when I read it, then it still has its "Adding a quantity" section showing how to register a new quantity.
- AC-D.2: Given the README, when I read it, then it has a section "Distance" showing `conv --distance` usage, `conv -d --list` and the library call with `build_distance_registry()`.

None of these criteria is manual.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| CLI (`conv -d …`, `conv --distance …`) | yes | the deliverable |
| CLI without the flag | yes | must stay exactly as before |
| Python library | no | used through `convert` and `build_distance_registry()`, not changed here |
| README | yes | new `## Distance` section |
| Linux, Python 3.12 | yes | the only supported platform |

## Design

In `src/conv/cli.py`, `main` takes `-d` / `--distance` out of the argument
list wherever it appears, then runs the existing logic unchanged with the
distance registry in place of the default one: `--help`, `--list` (one line,
same format as today) and conversion through `convert(value, from, to,
registry=<distance registry>)`. The registry is passed by keyword or
positionally as the fourth argument; AC-7.9 accepts either, and checks it is
a registry whose only quantity is `distance`.

How `main` receives a test registry for distance mode is the developer's
choice — for example an extra `distance_registry: Registry | None = None`
parameter, `None` meaning `build_distance_registry()` (or a module-level
`DISTANCE_REGISTRY`). The existing `registry` parameter keeps its meaning for
the mode without the flag.

All F-3 rules carry over: the value is parsed as a float (a dash-prefixed
number after the flag, `-3`, is a value, not an option); NaN/inf are invalid
numbers; the result is rounded to 6 places and printed as `repr`, `-0.0` as
`0.0`; every invalid input prints one `conv: error:` line (usage errors add a
usage line before it) and returns 1, never a traceback. The negative-distance
error comes from `convert`'s `ConversionError` (feature `distance-library`).

Update `USAGE` / `HELP` so `--help` mentions `-d, --distance`. Without the
flag, an unknown-unit error for a distance unit may add a hint such as "use
--distance", as long as it stays one `conv: error:` line (AC-3.6).

In `README.md`, add a `## Distance` section, separate from `## Adding a
quantity` (which stays), with: a `conv --distance 1 mi km` example, the
`conv -d --list` command and its output, and a Python example using
`from conv.registry import build_distance_registry` and
`convert(1, "mi", "km", registry=build_distance_registry())`. The README test
in `tests/unit/test_readme.py` execs the Python block of the README; keep
the new example valid Python that runs.

## Affected modules and layers

- Modules: `src/conv/cli.py`, `README.md`
- Layers: `cli` (reads `registry`, calls `core`)
- Key types: `main`, `USAGE`, `HELP`, `build_distance_registry`

## UI

- Screens / entry points: `conv -d <value> <from> <to>`,
  `conv --distance …`, `conv -d --list`, `conv --help`;
  `conv.cli.main(["--distance", …])`.
- New reusable components: n/a
- Design link: n/a

## Data

- Schema or persisted-shape changes: no
- New or changed repositories, APIs, caches: `conv.cli.main` may gain an
  optional keyword parameter for the distance registry.

## Edge cases

- Negative numbers after the flag (parsed as a value, then rejected) and
  zero → AC-7.3.
- Flag position → AC-7.4.
- Temperature units in distance mode → AC-7.5.
- Distance units without the flag → unchanged behaviour (unknown unit,
  AC-3.6 and AC-6.8).
- Non-numeric, NaN, overflow → AC-7.5.
- Wrong argument count → AC-7.6.
- `--list` with and without the flag → AC-7.7 and AC-4.1.
- Output precision → AC-7.2.
- Offline / permissions: the tool touches no files or network.

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| Users type `conv 1 mi km` without the flag and get "unknown unit" | medium | the error may hint at `--distance`; `--help` mentions the flag (AC-7.8) |
| The flag handling changes plain `conv` / `conv --list` | low | the AC-3.x and AC-4.x acceptance tests keep running |
| `-d -3` is read as an option | medium | AC-7.3 tests it explicitly |

- Rollback: revert the feature's commits; nothing is persisted.

## Test plan

- Unit / integration: unit tests in `tests/unit/` for the flag handling in
  `main` with a fresh in-memory registry.
- End-to-end / UI: acceptance tests in `tests/acceptance/test_cli_distance.py`
  (subprocess runs of the installed `conv`, `main` with `convert` patched) and
  `tests/acceptance/test_distance_readme.py` (README sections);
  `uv run pytest tests/acceptance/test_cli_distance.py tests/acceptance/test_distance_readme.py`.

## Open questions

- None.

## Links

- Ticket: —
- Design: n/a
- Related specs: `specs/features/backlog/distance-library/spec.md` (built
  before this one); `specs/features/archive/cli-conversion/spec.md`,
  `specs/features/archive/list-units/spec.md`.
