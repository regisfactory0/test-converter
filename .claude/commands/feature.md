---
description: Feature pipeline — ba writes the spec, you approve, then developer → tester → qa
argument-hint: <ticket | none> <feature-name> <requirements…> | specs/issues/<slug>.md
allowed-tools: Agent, Read, Glob, Grep, Edit, AskUserQuestion, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(git rev-parse*), Bash(git branch --show-current), Bash(git mv *)
---

# Feature

Raw invocation: **$ARGUMENTS**

You orchestrate (`CLAUDE.md` § Orchestrator). Agents carry their own contract;
each brief adds the expected branch, the spec folder, and the stage items below.

## Arguments

- `$1` — ticket (this project uses no ticket system: `none`/`-` → `—`). If `$1` is neither a
  ticket, a "none" marker nor an issue path, the arguments look misordered: ask.
- `$2` — feature name; quote it if multi-word.
- Rest — requirements, handed to `ba` verbatim.
- Or a single `specs/issues/<slug>.md` path: its body is the requirements, its
  `ticket:` the ticket, `<slug>` the default name. If its `route:` is not
  `feature`, say which command it is routed to and stop.

Missing requirements → ask what the feature must do. A name is not a spec.
Missing ticket → `—`, no question.

## Scope guard

| The request is | Say this and stop |
|---|---|
| Something already built behaving wrong | "That's a bug — use `/bugfix`." |
| Restructuring without behaviour change | "That's a refactor — use `/refactor`." |
| Copy, string or dependency change | "Too small for a spec — dispatching `developer` directly." |

The guard holds mid-pipeline too: if the work changes shape, stop and name the
pipeline that fits.

## 1. Slug

Derive a 2–4 word slug from the name (never the ticket key) and check
`specs/features/{backlog,active,archive}/`. Taken in `active/` or `archive/` →
pick a distinct one. Already in `backlog/` → a pickup: at `ready` skip to
step 3; at `draft`, `ba` completes it in step 2.

## 2. `ba` writes the spec

Brief: requirements verbatim, name, slug, ticket, issue file path if any.
Deliverable `specs/features/backlog/<slug>/spec.md` from
`specs/_templates/feature-template.md`, `status: ready`, every section filled
or `n/a` with a reason, numbered pass/fail acceptance criteria. Say whether to
skip the risk section or `plan.md` only if the user asked to.

Read the spec when `ba` returns.

## 3. GATE — the user approves the spec

**Hard stop. Do not dispatch `developer` this turn.** Report:

- spec path and slug (the user may rename it now)
- the acceptance criteria, verbatim
- gating and affected modules, if any
- `ba`'s open questions and assumptions

A `draft` spec is not ready for the gate — send it back to `ba`.

## 4. On approval

**Pickup.** `git mv specs/features/backlog/<slug>/ specs/features/active/<slug>/`,
then set `status: approved` and `updated:` in the frontmatter. If the input was
an issue file, set `origin: issue/<slug>` and delete that file in the same
change.

Every brief from here gives the folder `specs/features/active/<slug>/`.

**4a. `developer`** — implement against the spec.
If it stops on a spec problem, do not continue: report to the user and offer to
send the spec back to `ba`.

**4b. `tester`** — after `developer`, with a summary of what changed. Tests
from the acceptance criteria and edge cases; full suite green.
Red because the code misses a criterion → back to 4a with the failures. After
two round trips, stop and report to the user.

**4c. `qa`** — after `tester` is green. Verify per criterion; do not archive in
this dispatch. Any fail → back to 4a.

**4d. Archive** — dispatch `qa` with "archive `<slug>`"
(`specs/README.md` § Archive).

## Finally

Report: what was built, the per-criterion verdict, the spec's location, the
edge cases covered and those still uncovered, anything deferred. Show
`git status --short` and wait. Never commit without an explicit request.
