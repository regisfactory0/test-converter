# Plan: README section on adding a quantity

Spec: [spec.md](spec.md)

## README

- [ ] Insert `## Adding a quantity` between `## Run` and `## Test` in
      `README.md`. Add lines only; leave every other line as it is (AC-5.1,
      AC-5.9).
- [ ] Model paragraph with `base = value * factor + offset`, plus `Unit` and
      `Quantity` field tables with defaults taken from `conv.registry`
      (AC-5.2).
- [ ] One `python` block: imports from `conv` and `conv.registry`,
      `registry = Registry()` (or `build_default_registry()`),
      `registry.register(Quantity(name="length", base="m", units=(...)))` with
      `m` and `km` (factor 1000), and
      `convert(1, "km", "m", registry=registry)  # 1000.0` (AC-5.3).
- [ ] Run the block on its own with `uv run python`; confirm exit 0 and no
      stderr (AC-5.3).
- [ ] Built-in quantities paragraph: `build_default_registry()` in
      `src/conv/registry.py`; picked up by `conv --list`, `conv <value> <from>
      <to>` and `convert()` with no other change; a runtime registry is used
      only where passed (AC-5.4).
- [ ] Rules: case-insensitive uniqueness of symbol, name and alias, so
      `register` raises `ValueError` and leaves the registry unchanged;
      cross-quantity conversion raises `ConversionError` (AC-5.5).
- [ ] Pinned expectations: AC-4.1 (`tests/acceptance/test_list.py`), AC-2.1
      and `tests/unit/test_registry.py`; a change request adding a built-in
      quantity updates them in its spec change (AC-5.6).

## Test

- [ ] Add `tests/unit/test_readme.py`. It slices `README.md` from
      `## Adding a quantity` to the next `## ` heading, takes the single
      `python` block, `exec`s it in a fresh namespace, and asserts
      `convert(1, "km", "m", registry=namespace["registry"]) == 1000.0`. It
      fails when the heading or block is missing (AC-5.7).

## Verify

- [ ] `git diff main -- src tests/acceptance pyproject.toml` is empty (AC-5.8).
- [ ] `git diff main -- README.md` shows only added lines (AC-5.9).
- [ ] `uv run pytest`, `uv run ruff check .` and `uv run ruff format --check .`
      all pass (AC-5.10).
