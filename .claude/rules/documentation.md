---
paths:
  - "specs/**/*.md"
  - "docs/**/*.md"
---

# Documentation

Rules for Markdown in `specs/` and `docs/`.

## Diagrams

**Mermaid is the only diagram format.** No box art, arrows or trees drawn in a
code fence — they rot the moment a label changes.

| Explaining | Use |
|---|---|
| A message exchange between components or systems | `sequenceDiagram` |
| A lifecycle with named states | `stateDiagram-v2` |
| Branching logic or a decision path | `flowchart TD` |
| Module or layer dependencies | `flowchart LR` |
| Data schema relationships | `erDiagram` |

- Draw one only when prose cannot carry the shape. Two boxes and an arrow is a
  sentence.
- Short node labels; detail goes in the prose.
- Quote node labels containing `(`, `)`, `:`, `,` or `-`: `A["retry (max 3)"]`.
  Do not quote edge text in `stateDiagram-v2` or message text in
  `sequenceDiagram` — the quotes render literally.
- No `%%{init}%%`, `classDef` colours or themes; they break across renderers and
  dark mode.
- A diagram changes in the same change as the flow it shows.

**Exception:** byte- and bit-level wire layouts use a table of
`field / offset / width / meaning`. Flows, states and sequences are always
Mermaid.

## Directory layouts

A table or a nested list, never a box-drawing tree.

## References

- Reference code by symbol — `ClassName`, `ClassName.member`, `CONSTANT_NAME`.
  Add a path only when the name is ambiguous. Never a line number in a spec.
- `path:line` belongs only in point-in-time records: `issues.md`,
  `specs/issues/*.md`, hardware runbooks, agent reports.
- State a constant with its value and source, so a reader can verify it.
- Link to the authoritative document instead of restating it. Copies drift.

## Prose

- Tables for enumerable facts; prose for behaviour and reasoning.
- No hard-coded counts ("the twelve features") — they go stale with the next
  entry.
