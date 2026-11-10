---
title: <Refactor name>
status: draft          # draft | ready | approved | in-progress | done | dropped
ticket: —              # this project uses no ticket system
origin: —              # issue/<slug> if promoted from specs/issues/
# dropped: <reason>    # only when status: dropped
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: <name>
---

# <Refactor name>

<!-- Structure changes; behaviour does not. If observable behaviour should
     change, use feature-template.md. Fill every section, or `n/a` and why. -->

## Current state

<!-- What exists today and where. Name the types. -->

## Problems

<!-- Concrete cost: what is hard to change, breaks repeatedly, or cannot be
     tested. "Not clean" is not a problem. -->

-

## Target state

<!-- What it looks like afterwards, and why that shape is better. -->

## Out of scope

-

## Behaviour preservation

<!-- Replaces acceptance criteria. Numbered so verification can cite them. -->

**Tests that must pass unchanged:**
<!-- Name them. No coverage → characterisation tests first, listed here. -->
-

**Observable behaviour that must not shift:**
<!-- Ordering, timing, state transitions, errors surfaced to users, persisted
     data shape, events emitted. -->
1.

**Accepted behaviour changes:** none

## Migration steps

<!-- Ordered; each one builds, passes tests, and is reviewable alone. -->

1.
2.

## Affected modules and layers

- Modules:
- Layers:
- Public API changes across modules: <yes — every call site / no>

## Edge cases

<!-- Paths most likely to change behaviour silently: error handling, lifecycle
     and teardown, concurrency, reflection or DI lookups by name. -->

-

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| | | |

- Rollback:
- Ships in stages, or all-or-nothing:

## Test plan

- Existing tests covering the area:
- Characterisation tests required first:

## Open questions

-

## Links

- Ticket:
- Related specs:
