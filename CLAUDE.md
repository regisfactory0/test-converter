# test-converter

`conv` is a small command-line tool and Python library that converts values
between units; version 1 knows one quantity, temperature (Celsius, Fahrenheit,
Kelvin), so `conv 100 C F` prints `212.0`. Units live as data in a per-quantity
registry, so later versions can add length, mass or volume without rewriting
the CLI or the library.

## Always know

- No external services, no network, no file writes, no runtime dependencies:
  `pyproject.toml` keeps `dependencies = []`. Tests need no test doubles beyond
  a fresh in-memory registry instance where they need extra quantities.
- Public names are fixed: `conv.convert`, `conv.ConversionError` (a subclass of
  `ValueError`) and `conv.cli.main(argv, registry) -> int`; the console script
  `conv` points at `conv.cli.main`.
- Units are affine to their quantity's base unit: `base = value * factor + offset`
  (temperature base is kelvin). A quantity may carry a minimum base value
  (temperature: 0 K, with a 1e-9 K tolerance at the boundary).
- Units match case-insensitively by symbol or full name (`C`, `c`, `celsius`);
  no degree sign, no plurals.
- The library returns full-precision floats; only the CLI rounds (6 places,
  printed as the `repr` of the rounded float, `-0.0` as `0.0`).
- Every invalid input, including a wrong argument count, exits 1 (not
  argparse's 2) with a one-line `conv: error: …` on stderr and no traceback.

## Stack

Python 3.12 (pinned in `.python-version`), managed with uv; standard library
only at runtime; package `conv` in `src/conv/`, built with `uv_build`; console
script `conv` in `[project.scripts]`; pytest for unit (`tests/unit`) and
acceptance (`tests/acceptance`) tests; ruff for lint and format.

Architecture: layered library with a thin CLI. Dependency direction: `cli` → `core` → `registry`.
Rules for writing code against it: `.claude/rules/architecture.md`.

## Commands

| Task | Command |
|---|---|
| Build | `uv build` |
| All tests | `uv run pytest` |
| One test | `uv run pytest <pattern>` |
| Lint | `uv run ruff check .` |
| Format check | `uv run ruff format --check .` |

Environment: `uv sync`. Run these in the foreground with a
10-minute timeout — never in the background.

## Principles

- **Simplicity first.** The smallest change that solves the problem.
- **Root causes.** No temporary fixes, no symptom suppression.
- **Minimal impact.** Touch only what the task needs.

## Rules and specs

| File | Loads | Covers |
|---|---|---|
| `.claude/rules/code-style.md` | source and test files | Conventions, naming, comments, errors |
| `.claude/rules/architecture.md` | source files | Layers, boundaries, dependencies |
| `.claude/rules/git.md` | always | Commits, staging, branches, PRs |
| `.claude/rules/documentation.md` | Markdown in `specs/`, `docs/` | Diagrams, references, prose |
| `specs/README.md` | on demand | Spec lifecycle, when a spec is required, issues |

## Orchestrator — main session only

> Agents dispatched through the Agent tool skip this section. Their rules are
> the contract in their own agent file.

**You orchestrate; agents do the work.** You dispatch, carry results between
stages, and judge reports. You may read specs, `git status`/`log`/`diff`, and
grep to write a good brief or classify a request. You do not write production
code, tests or specs yourself, and you do not re-run an agent's build or tests.

| Agent | Use for | Deliverable |
|---|---|---|
| `ba` | Requirements, specs, feasibility, issue triage | Spec in `specs/features/backlog/` |
| `developer` | Implementation, diagnosis, fixes | Source code |
| `tester` | Unit and integration tests, baselines | Test files, test run results |
| `qa` | Verification against acceptance criteria, archiving specs | Per-criterion report |

| Request | Route |
|---|---|
| New or changed behaviour | `/feature` |
| Something built behaves wrong | `/bugfix` |
| Restructure without behaviour change | `/refactor` |
| Copy or string change, dependency bump, single-file tweak | `developer` directly |
| Fits none of these | Ask the user — do not guess |

- **Outside a pipeline, describe the approach and wait for approval** before
  any change to code. Inside a pipeline, its gates are the approvals.
- **Ask when requirements are ambiguous** — before dispatching, not after.
- **Briefs are self-contained.** Agents share no memory. Every brief names the
  expected branch (`git branch --show-current`), the spec folder or issue file,
  and what done looks like. Do not restate the agent contract; it is in the
  agent file.
- **Dispatch independent work in parallel**, in one message.
- **Verify before relaying.** Check an agent's file changes with `git diff`
  before acting on its report; a report can be consistent and wrong.
- **Work that changes shape mid-pipeline stops the pipeline.** Name the
  pipeline that fits the new shape before dispatching again.
- **When the user corrects you,** propose an edit to the rule file that would
  have prevented it, in the same session.
- **After code changes,** list the edge cases handled and the ones still
  uncovered.
- **Never commit or push without an explicit request** (`.claude/rules/git.md`).
