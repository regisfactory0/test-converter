---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Code style (Python)

The language part of `.claude/rules/code-style.md` for this module kind.

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
