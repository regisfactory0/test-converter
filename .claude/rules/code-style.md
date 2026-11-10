---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Code style

## Conventions

- Match the surrounding code. Before creating or editing a file, read its
  siblings for structure, naming and idiom, and follow them over any general
  preference.
- Reuse before writing: search for an existing component, helper or extension
  first.
- Descriptive names. Abbreviate only where the abbreviation is the domain's
  own word.
- Formatting and lint are enforced by `uv run ruff check .` and `uv run ruff format --check .`; do not
  hand-format against them.

## Python

- Python 3.12 only; the version is pinned in `.python-version` and
  `requires-python`. Use 3.12 syntax: built-in generics (`list[str]`), `X | None`
  unions — ruff's `UP` rules enforce it.
- Type hints on every function signature, including `-> None` (as in
  `tests/unit/test_package.py`).
- Line length 100, imports sorted by ruff (`I`); `uv run ruff format .` is the
  formatter, never hand-alignment.
- Standard library only at runtime: `[project] dependencies` stays `[]`; dev
  tools go in the `dev` dependency group via `uv add --dev`.
- src layout: the importable package is `src/conv/`; tests import it as `conv`
  (installed by `uv sync`), never through `sys.path` tweaks.
- Naming: `snake_case` modules, functions and variables; `PascalCase` classes;
  `UPPER_SNAKE` module constants.
- Public API is what `conv/__init__.py` re-exports; anything else is internal.
- Tests are plain pytest functions with bare `assert`, in `test_*.py` files
  under `tests/unit/` or `tests/acceptance/`; pytest runs with
  `--import-mode=importlib`, so test packages need no `__init__.py`.

## Errors

- Model expected failures as values (a result type, sealed hierarchy or error
  enum — whichever the codebase already uses). Do not introduce a parallel error
  type for a new area.
- Let exceptions cross only system boundaries: network, storage, device, OS.
- Never swallow an error to make a symptom go away.

## Comments

Default: none. Names carry meaning; a comment admits they failed.

Write one only for a non-obvious *why*: a workaround, an ordering constraint, a
hazard (race, lifetime, a call that must not move), or a decision whose
alternative looked equally valid.

- Max 2 lines.
- Never name a spec, plan, ticket, migration step or test-suite number.
- No history — git has it. No restating the code. No banners.
- Doc comments only where a public contract is not obvious from the signature.
- Test names state the behaviour they pin; comment only a fixture subtlety the
  name cannot carry.
