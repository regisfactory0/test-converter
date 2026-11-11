---
title: CLI conversion
status: done
ticket: —              # this project uses no ticket system
origin: —
created: 2026-11-10
updated: 2026-11-11
owner: developer
---

# CLI conversion

## Problem

The library can convert temperatures, but there is no command to do it from a
terminal. *As a CLI user, I want `conv <value> <from> <to>` to print the
converted value, so that I get an answer in one command.* Priority: `must`.

## Scope

**In scope:**
- `conv.cli.main(argv: list[str] | None = None, registry=None) -> int`, the
  entry point of the `conv` console script (`[project.scripts]` in
  `pyproject.toml`, already declared as `conv = "conv.cli:main"`).
- `conv <value> <from> <to>`: parse the value, call the library's `convert`,
  print the rounded result.
- `conv --help`: usage on stdout, exit 0.
- Every invalid input (bad number, unknown unit, below absolute zero, overflow,
  wrong argument count, unknown option) → one `conv: error: …` line on stderr,
  exit 1, no traceback.

**Out of scope:**
- `conv --list` (its own feature, built after this one).
- Interactive mode, reading values from stdin or files, several values at once.
- Precision flags, localisation (decimal comma, translated messages).
- Any conversion logic in the CLI: it lives in the library.

## Acceptance criteria

- AC-3.1: Given the installed CLI, when I run `conv 100 C F`, then stdout is exactly `212.0\n`, stderr is empty and the exit code is 0.
- AC-3.2: Given the CLI, when I run `conv 100 F C`, then stdout is `37.777778\n` (result rounded to 6 decimal places, printed as Python `repr` of the rounded float, so trailing zeros are dropped but at least one decimal remains).
- AC-3.3: Given the CLI, when I run `conv -40 C F` (negative value as first argument), then stdout is `-40.0\n` and exit code 0.
- AC-3.4: Given the CLI, when I run `conv 0 C K`, then stdout is `273.15\n`; and `conv 1e3 K C` prints `726.85\n`.
- AC-3.5: Given an invalid number (`conv abc C F`, `conv "" C F`, `conv nan C F`, `conv inf C F`), when I run it, then stderr has a single line starting with `conv: error:`, stdout is empty and the exit code is 1.
- AC-3.6: Given an unknown unit (`conv 10 C X`), when I run it, then stderr has a single line starting with `conv: error:` naming `X`, and the exit code is 1.
- AC-3.7: Given a value below absolute zero (`conv -500 F C`), when I run it, then stderr has a single line starting with `conv: error:` mentioning absolute zero, and the exit code is 1.
- AC-3.8: Given the wrong number of arguments (none, one, two, or four), when I run `conv`, then stderr shows a short usage line plus a `conv: error:` line, and the exit code is 1 (not argparse's default 2).
- AC-3.9: Given `conv --help`, when I run it, then usage text goes to stdout and the exit code is 0.
- AC-3.10: Given the CLI module, when I call its `main(argv)` entry point with a list of arguments, then it returns the exit code and calls the library's `convert` (verified by a test that patches `convert`), so the CLI holds no conversion logic.
- AC-3.11: Given any invalid input, when the CLI fails, then no Python traceback is printed.

None of these criteria is manual.

Also checked here (non-functional requirements of the product):
- **Performance:** `conv 100 C F` finishes in under 0.5 s (a timed subprocess run).
- **Security:** no runtime dependencies (`pyproject.toml` `dependencies = []`);
  no network access, no file writes.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| CLI (`conv` console script) | yes | the deliverable |
| Python library | no | used, not changed |
| Linux, Python 3.12 | yes | the only supported platform |

## Design

`src/conv/cli.py` (stubbed) holds `main`. Dependency direction `cli` → `core`;
the CLI never touches unit factors or offsets.

- **Calling the library.** `cli.py` imports `convert` at module level
  (`from conv.core import convert`) and calls it through that module-level
  name as `convert(value, from_unit, to_unit, registry=registry)`. The
  acceptance test patches `conv.cli.convert` and expects it to be called with
  the parsed float and the two unit strings as the first three positional
  arguments.
- **Parsing.** The parser is the developer's choice (`argparse` or
  hand-rolled). Constraints: a negative number such as `-40` is a value, not
  an option (AC-3.3); the number is parsed with `float()` by the CLI itself,
  not argparse's `type=float`, so that a bad number gives exactly one stderr
  line (AC-3.5); NaN and infinity are rejected; wrong argument counts and
  unknown options print a short usage line plus a `conv: error:` line and
  exit 1, never argparse's 2 (subclass `ArgumentParser` and override `error`,
  or similar). `--help` prints usage to stdout and returns 0. `main` returns
  the exit code instead of calling `sys.exit`, including for usage errors
  (catch `SystemExit` from argparse if used).
- **Output.** `round(result, 6)`, printed as its `repr`; `-0.0` prints as
  `0.0` (e.g. `conv 32 F C` → `0.0`).
- **Errors.** A `ConversionError` from `convert` becomes
  `conv: error: <message>` on stderr and exit 1. An overflow (`conv 1e308 C F`)
  arrives as a `ConversionError` from the library (it never returns `inf`).
  Messages are one line and name the offending value or unit.
- `registry=None` means the library's default registry; it is passed through
  to `convert` unchanged.

## Affected modules and layers

- Modules: `src/conv/cli.py`; `pyproject.toml` (console script, already declared)
- Layers: `cli`
- Key types: `main`

## UI

- Screens / entry points: the `conv` command; `conv.cli.main(argv)`.
- New reusable components: n/a
- Design link: n/a

Output formats, exactly: result line on stdout (`212.0\n`); errors as one
line on stderr starting `conv: error:`; usage errors add a short usage line
before it.

## Data

- Schema or persisted-shape changes: no
- New or changed repositories, APIs, caches: none

## Edge cases

- Negative numbers parsed as options → AC-3.3.
- Empty input → AC-3.5 (`conv "" C F`), AC-3.8 (no arguments).
- Non-numeric, NaN, inf → AC-3.5.
- Overflow (`conv 1e308 C F`) → handled by the library (AC-1.9), surfaces as
  an AC-3.5-style error, exit 1.
- Unknown unit → AC-3.6.
- Below absolute zero → AC-3.7.
- Wrong argument count → AC-3.8.
- Output precision and `-0.0` → AC-3.2.
- Offline / permissions: the tool touches no files or network.

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| Negative values (`-40`) parsed as options by argparse | medium | AC-3.3 tests it explicitly |
| Float noise in output (`98.60000000000001`) | medium | rounding to 6 places, AC-3.2 |
| argparse's exit 2 or multi-line errors leak through | medium | AC-3.5, AC-3.8, AC-3.11 |

- Rollback: revert the feature's commits; nothing is persisted.

## Test plan

- Unit / integration: unit tests in `tests/unit/` for argument parsing and
  output formatting through `main(argv)`.
- End-to-end / UI: acceptance tests in `tests/acceptance/test_cli.py` run the
  installed `conv` script as a subprocess (after `uv sync`) and call `main`
  directly; `uv run pytest tests/acceptance/test_cli.py`.

## Open questions

- None.

## Links

- Ticket: —
- Design: n/a
- Related specs: `specs/features/archive/temperature-library/spec.md` (built
  before this one), `specs/features/backlog/list-units/spec.md`
