---
paths:
  - "tests/**/*.py"
---

# Testing

The test rules of this module kind. `tester-backend` writes tests by them;
`qa` reads them for the frameworks and commands before it runs anything.

## Conventions

- Frameworks: pytest. Tests live in `tests/**/*.py`, mirroring the
  source layout of what they test.
- Names state behaviour: `returns cached value when offline`.
- No real network, device, clock or filesystem in unit tests — fakes and mocks
  through constructor injection; virtual time instead of sleeps.
- Every test has a meaningful assertion and resets shared state.
- Do not add a test dependency without approval.

## Running

- One test or class while iterating: `uv run pytest <pattern>`.
- Before reporting green: the tests you wrote or changed and the existing tests
  of the code the change touches, plus `uv run ruff check .`.
- Not the full suite (`uv run pytest`): it runs once, at the end of the work
  (`CLAUDE.md` → *Test runs*), unless the brief says this run is that final
  check.
- A failure that moves between runs is a leak or ordering problem — report the
  suspected test rather than re-running until green.
