---
title: Registry.register skips base and empty-units checks
type: gap
severity: low
area: registry
origin: fixes-1
found: 2026-11-11
ticket: —
route: bugfix
---

# Registry.register skips base and empty-units checks

## Observed

`Registry.register` does not check that `Quantity.base` names one of the quantity's units, or that `units` is not empty.

## Evidence

- src/conv/registry.py:38

## Why it matters

A malformed quantity registers silently and fails later.

## Notes

Migrated from fixes-1 issues.md at archive.
