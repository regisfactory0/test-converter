---
title: A unit with factor=0 makes convert raise ZeroDivisionError
type: bug
severity: medium
area: registry
origin: fixes-1
found: 2026-11-11
ticket: —
route: bugfix
---

# A unit with factor=0 makes convert raise ZeroDivisionError

## Observed

A unit with `factor=0` passes `Registry.register`. Converting to it raises `ZeroDivisionError` instead of `ConversionError`, and the CLI prints a traceback. It should be rejected at registration or reported as `ConversionError`.

## Evidence

- src/conv/core.py:50
- src/conv/registry.py:38

## Why it matters

Breaks the rule that every invalid input exits 1 with a one-line error and no traceback.

## Notes

Migrated from fixes-1 issues.md at archive.
