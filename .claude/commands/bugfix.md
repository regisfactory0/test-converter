---
description: Bug pipeline — developer diagnoses, you confirm the cause, then failing test → fix → verify
argument-hint: <ticket | none> <bug-name> <symptom, repro steps, expected vs actual…> | specs/issues/<slug>.md
allowed-tools: Agent, Read, Glob, Grep, AskUserQuestion, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(git rev-parse*), Bash(git branch --show-current)
---

# Bug fix

Raw invocation: **$ARGUMENTS**

You orchestrate (`CLAUDE.md` § Orchestrator). Agents carry their own contract;
each brief adds the expected branch and the stage items below.

No spec is written. Out-of-scope findings go to `specs/issues/<slug>.md`
(`specs/README.md` § Issues).

## Arguments

- `$1` — ticket (this project uses no ticket system: `none`/`-` → `—`). Neither → ask.
- `$2` — short bug name.
- Rest — symptom text, handed over verbatim. Never edit a cause into it.
- Or a single `specs/issues/<slug>.md` path: its Observed and Evidence are the
  symptom. `route: feature` or `refactor` → say which command and stop.

No symptom → ask what goes wrong and how to reproduce it. A name is not a bug
report.

## Scope guard

"It doesn't do X yet" is a feature (`/feature`). "It does X wrong" or "it used
to do X" is a bug. Ugly but working code is a refactor (`/refactor`). Unsure →
ask; do not pick.

## 1. `developer` diagnoses

Brief: symptom verbatim, name, ticket. **Diagnose only — no edits.** Report the
root cause as `path:line`, the mechanism, why it produces exactly this symptom,
the blast radius, confidence, and rival explanations not ruled out. If the
symptom cannot be located, say what is needed (a log, a version, repro data).

## 2. GATE — the user confirms the cause

Report the cause in plain language, the evidence, confidence, rivals, and blast
radius. Wait for confirmation.

**Fast path:** skip the wait only when all hold — high confidence, no rival, the
fix stays in one file, nothing else reads the faulty code. Say in one line that
you are taking the fast path, then continue.

## 3. `tester` writes the failing test

Brief: confirmed cause, `path:line`, symptom. Bug mode: narrowest layer, asserts
the correct behaviour, shown failing for the right reason. Passes before the
fix → the diagnosis is wrong: back to step 1.

## 4. `developer` fixes

Brief: cause, test path, its failure output. Fix the root cause with the
smallest change; no workarounds, no swallowed errors, no tidying nearby. Never
edit the test — if it is wrong, stop and report. Run the test green, then the
full suite.

## 5. Verify

User-visible symptom → dispatch `qa` with the symptom, cause and changed files
to confirm the symptom is gone and adjacent flows hold. Internal-only fix →
`tester`'s green suite is the verification.

On pass, the verifying agent deletes the input issue file, if any, in the same
change — say so in its brief.

## Finally

Report: the cause in one or two sentences, what changed and why it is the cause
and not a symptom, the repro test (failed before, passes now), the verification
verdict, edge cases covered and still open. Show `git status --short` and wait.
