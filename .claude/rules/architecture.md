---
paths:
  - "src/**/*.py"
---

# Architecture

Rules for **writing** code. What currently exists belongs in the code and
not here; inventories restated in rules drift.

## Structure

- Layered library with a thin CLI. Dependencies point one way: **`cli` → `core` → `registry`**.
  A dependency against that direction is a bug, not a style choice.
- Stick to the existing directory structure. A new top-level folder or package
  root needs approval.
- Adding, removing or upgrading a dependency needs approval.
- One responsibility per unit: a service, module or class owns one concern.
- Platform- or variant-specific behaviour lives in its own implementation
  behind a shared interface, not in a `switch` on platform at each call site.

## Async and state

- Respect structured concurrency: work runs in a scope that owns its lifetime.
  No fire-and-forget global scopes.
- State has one owner. Model multi-step lifecycles as an explicit state
  machine, not a set of booleans.
