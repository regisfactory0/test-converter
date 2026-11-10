# Git

## Writes need the user

- **Never commit or push** unless the user asks in this session. Approval for
  one commit does not carry to the next.
- **Never amend, rebase, force-push, reset, clean, or delete a branch** without
  explicit approval.
- Before any operation that could lose uncommitted work, say so and wait.
- Never run a bare `git stash pop` — if `git stash push` had nothing to stash,
  it pops an unrelated older stash.
- Agents run no git writes at all (their contract). The one exception is a
  `git mv` of a spec folder when the brief names it.

## Staging

- Stage only when committing, and stage files by name — never `git add -A` or
  `git add .`.
- Review `git status` before staging.
- Never stage secrets: `.env*`, keys and certificates.

## Branches

- Default branch: `main`. PRs target `main` unless
  told otherwise.
- Naming: `feature/<slug>`, `bugfix/<slug>`, `refactor/<slug>`.
- Never work directly on `main`; branch first.
- Check the current branch live (`git branch --show-current`) before briefing an
  agent or committing — a session-start snapshot goes stale.

## Commit messages

Short imperative subject, capitalised, no trailing period. No ticket ids. No
AI attribution trailers. Example: `Add the price alert command`.

- Imperative mood, 1–2 sentences, focused on **why**.

## Pull requests

- Concise: what changed and why.
- No change statistics, no test-plan checklist, no template sections.
