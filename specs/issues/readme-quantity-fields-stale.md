---
title: README "Adding a quantity" omits the newer Quantity fields
type: gap
severity: low
area: README
origin: ad hoc
found: 2026-11-21
ticket: —
route: bugfix
---

# README "Adding a quantity" omits the newer Quantity fields

## Observed

The `Quantity` field table under `## Adding a quantity` lists `name`, `base`,
`units` and `min_base` only. `Quantity` also has `min_tolerance` and
`below_min_message` (both default `None`), added with the distance registry.
The section therefore no longer names "every field as defined in
`conv.registry`" (AC-5.2 in `specs/system/features.spec.md`). It should list
both fields with their defaults and meaning.

## Evidence

- README.md:85
- src/conv/registry.py:29
- src/conv/registry.py:30

## Why it matters

A maintainer adding a quantity with a minimum cannot learn from the README how
to set the tolerance or the error message. `tests/unit/test_readme.py` runs
only the example, so nothing catches the gap.

## Notes

Found while carrying the archived specs into the system specs
(spec-cleanup). Fixing it means adding lines to `README.md`, so the change is
small. AC-5.2 is listed under *Still to check* until it is fixed.
