---
description: Refactor pipeline — green baseline first, spec, architect and gate only across boundaries, then developer → tester proves nothing changed
argument-hint: <ticket | none> <refactor-name> <what to change and why…> | specs/issues/<slug>.md
allowed-tools: Agent, Read, Glob, Grep, Edit, AskUserQuestion, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(git rev-parse*), Bash(git branch --show-current), Bash(git mv *)
---

# Refactor

Raw invocation: **$ARGUMENTS**

You orchestrate (`CLAUDE.md` § Orchestrator). Agents carry their own contract;
each brief adds the expected branch, the spec folder or issues location, and the
stage items below.

**Behaviour does not change.** Every stage exists to prove it.

`developer` and `tester` below are the *Developer* and *Tester* of each module
the refactor touches (`CLAUDE.md` → *Modules*, by the module's *Path*). For
several modules, dispatch them one after the other, in the table's order.

## Arguments

- `$1` — ticket (this project uses no ticket system: `none`/`-` → `—`). Neither → ask.
- `$2` — refactor name; becomes the slug if a spec is needed.
- Rest — what to change and why, handed over verbatim.
- Or a single `specs/issues/<slug>.md` path with `route: refactor`; any other
  route → say which command and stop.

No description → ask what should change and what problem it solves.

## Scope guard

A behaviour change is a feature (`/feature`); something broken is a bug
(`/bugfix`). A refactor that "also fixes" something is two pieces of work —
split them and say so.

## 1. Classify

Grep the actual reach; do not decide from the description. A spec is required
per `specs/README.md` § When a spec is required. State the branch you took in
one line.

**Spec branch.** Dispatch `ba` for `specs/features/backlog/<slug>/spec.md` from
`specs/_templates/refactor-template.md`, with individually buildable migration
steps and a concrete behaviour-preservation list.

When the refactor crosses a module or public-API boundary, then dispatch
`architect` with the spec: it updates `specs/system/architecture.spec.md` and
`.claude/rules/architecture.md` to the target state, and files issues for the
gaps it finds.

Then **hard stop** with the target state, steps, affected modules, rollback and,
across a boundary, the architecture diff, and wait for approval: the approval
covers the spec and the architecture. On approval: `git mv` to
`specs/features/active/<slug>/`, set `status: approved`; when `architect` gave a
new `Architecture:` line, put it into `CLAUDE.md`.

## 2. `tester` — green baseline first

Before any code moves. Refactor mode: exact baseline counts, characterisation
tests for uncovered affected paths, new counts. Red baseline → stop and report.

## 3. `developer` refactors

Brief: description, spec folder if any, baseline counts, characterisation test
paths. No behaviour change, no fixes, no "while I was here". Tests may move with
their class; assertions stay byte-identical. Follow the migration steps if a
spec exists. No new dependencies.

## 4. Prove nothing changed

`tester` re-runs and compares: passing count ≥ baseline, zero new failures, no
assertion changed (`git diff` of the test directories). A changed assertion is a
behaviour change — the refactor failed.

User-visible flows through the affected code → then dispatch `qa` to confirm
they behave as before, per flow.

Spec branch: archive as `/feature` step 4 does once everything is green.

## Finally

Report: spec or not, baseline before → after as numbers, what moved and the
dependency direction now, confirmation no assertion changed, verification
verdict, and behaviour that looks wrong (recorded as issues for `/bugfix`).
Show `git status --short` and wait.
