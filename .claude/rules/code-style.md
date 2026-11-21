---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Code style

## Conventions

- Match the surrounding code. Before creating or editing a file, read its
  siblings for structure, naming and idiom, and follow them over any general
  preference.
- Reuse before writing: search for an existing component, helper or extension
  first.
- Descriptive names. Abbreviate only where the abbreviation is the domain's
  own word.
- The language conventions, lint and format of a module are in its
  `code-style-<kind>.md` (`CLAUDE.md` → *Modules*).

## Errors

- Model expected failures as values (a result type, sealed hierarchy or error
  enum — whichever the codebase already uses). Do not introduce a parallel error
  type for a new area.
- Let exceptions cross only system boundaries: network, storage, device, OS.
- Never swallow an error to make a symptom go away.

## Comments

Default: none. Names carry meaning; a comment admits they failed.

Write one only for a non-obvious *why*: a workaround, an ordering constraint, a
hazard (race, lifetime, a call that must not move), or a decision whose
alternative looked equally valid.

- Max 2 lines.
- Never name a spec, plan, ticket, migration step or test-suite number.
- No history — git has it. No restating the code. No banners.
- Doc comments only where a public contract is not obvious from the signature.
- Test names state the behaviour they pin; comment only a fixture subtlety the
  name cannot carry.
