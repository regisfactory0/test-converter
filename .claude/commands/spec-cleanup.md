---
description: Spec cleanup pipeline — ba carries archived specs into the system specs, you approve, then ba removes them and every reference → qa
argument-hint: <slug…> | all
allowed-tools: Agent, Read, Glob, Grep, Edit, AskUserQuestion, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(git rev-parse*), Bash(git branch --show-current), Bash(git mv *)
---

# Spec cleanup

Raw invocation: **$ARGUMENTS**

You orchestrate (`CLAUDE.md` § Orchestrator). Agents carry their own contract;
each brief adds the expected branch, the slugs, and the stage items below.

An archived spec is history, and Git keeps history. Once the as-built system
specs carry what it said, the archived copy goes. What a reference is, and how
each one is repointed or removed: `specs/README.md` § Cleanup.

## Arguments

- One or more slugs of folders in `specs/features/archive/`.
- Or `all` — every folder in `specs/features/archive/` whose `spec.md` says
  `status: done` or `status: dropped`.

No argument → ask which specs to remove. An `all` that finds no such folder →
say there is nothing to remove and stop.

## Scope guard

Check every slug before any file changes:

| The slug is | Say this and stop |
|---|---|
| Not a folder in `specs/features/archive/` | "`<slug>` is not archived — only archived specs are removed." |
| Archived, but its `spec.md` is not `done` or `dropped` | "`<slug>` is `<status>` — only done or dropped specs are removed." |

The pipeline removes specs; it is not a general tidy-up of `docs/`,
`specs/issues/` or the system specs. Work that changes code behaviour is a
`/feature`, `/bugfix` or `/refactor`.

## 1. `ba` migrates open issues

Brief: the slugs. Each spec's `issues.md` per `specs/README.md` § Archive step 1:
every open item becomes a file in `specs/issues/`.

## 2. `ba` carries each spec into the system specs

Brief: the slugs, `specs/README.md` § Cleanup. For each spec, the as-built
system specs carry its lasting content: behaviour, decisions with their
reasons, constraints, and every criterion not yet verified, named there as
still to check.
They are the files in `specs/system/`; `ba` changes only what each spec needs.

Deliverable: the system-spec diff and, per slug, one line on where its content
now lives. Read the diff when `ba` returns.

## 3. GATE — the user approves the removal

**Hard stop. Do not dispatch the removal this turn.** Report:

- the slugs to remove, each with its folder
- per slug, where its content now lives, and every criterion carried as still
  to check
- the system-spec diff (`git diff --stat`, then the changed sections)
- the issue files step 1 created

## 4. On approval: `ba` removes the specs

Brief: the slugs, `specs/README.md` § Cleanup. `ba` deletes each folder and
repoints or removes every reference to it. A reference in source or test code
goes into the brief of the *Developer* (source) or the *Tester* (test code) of
the module whose *Path* holds the file (`CLAUDE.md` → *Modules*), through `ba`'s
report; dispatch them with it.

## 5. Verify

Dispatch `qa`: per removed slug, its content is carried, no reference is left
(`specs/README.md` § Cleanup), and the full suite (`uv run pytest`) is green.
Any fail → back to step 4 with the failures.

## Finally

Report: the specs removed, where each one's content now lives, the criteria
carried as still to check, the issue files created. Show `git status --short`
and wait. Never commit without an explicit request.
