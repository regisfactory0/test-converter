---
title: Registry.register accepts duplicate quantity names
type: gap
severity: low
area: registry
origin: fixes-1
found: 2026-11-11
ticket: —
route: bugfix
---

# Registry.register accepts duplicate quantity names

## Observed

`Registry.register` accepts two quantities with the same name. `--list` prints both lines and the cross-quantity error message is ambiguous.

## Evidence

- src/conv/registry.py:50

## Why it matters

Output and error messages become ambiguous.

## Notes

Migrated from fixes-1 issues.md at archive.
