---
title: <Feature name>
status: draft          # draft | ready | approved | in-progress | done | dropped
ticket: —              # this project uses no ticket system
origin: —              # issue/<slug> if promoted from specs/issues/
# dropped: <reason>    # only when status: dropped
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: <name>
---

# <Feature name>

<!-- Fill every section, or write `n/a` and why. Discoveries go in issues.md
     beside this file, never here. Diagrams are Mermaid. -->

## Problem

<!-- What is missing or broken today, and for whom. Not the solution. -->

## Scope

**In scope:**
-

**Out of scope:**
<!-- What a reader might reasonably assume is included but is not. -->
-

## Acceptance criteria

<!-- Numbered, each objectively pass/fail. "Works reliably" is not a criterion;
     "shows the saved value within 1 s of reopening the screen" is. -->

1.
2.
3.

## Applicability

| Platform / variant / tier | Applies | Notes |
|---|---|---|
| | yes / no | |

<!-- A claim to verify against the code, not an assumption. -->

## Design

<!-- The approach in a few paragraphs: where the change sits, the main types,
     data flow. A diagram only if prose cannot carry it. -->

## Affected modules and layers

- Modules:
- Layers:
- Key types:

## UI

<!-- n/a for non-UI work. -->

- Screens / entry points:
- New reusable components:
- Design link:

## Data

- Schema or persisted-shape changes: <yes — migration / no>
- New or changed repositories, APIs, caches:

## Edge cases

<!-- Required before implementation. Consider: failure mid-operation, missing
     permission, offline, concurrent use, empty and maximum inputs, the
     feature being unavailable. -->

-

## Risk and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| | | |

- Rollback:

## Test plan

- Unit / integration:
- End-to-end / UI:

## Open questions

<!-- Empty means genuinely none. -->

-

## Links

- Ticket:
- Design:
- Related specs:
