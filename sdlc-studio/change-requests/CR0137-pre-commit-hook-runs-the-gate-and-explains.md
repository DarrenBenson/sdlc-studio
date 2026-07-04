# CR-0137: pre-commit hook runs the gate and explains every failure in detail (make enforcement un-skippable)

> **Status:** Complete
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature
> **Affects:** .githooks/pre-commit, tools/enable-hooks.sh, AGENTS.md, CONTRIBUTING.md, README.md
> **Depends on:** -

## Summary

The repo ships a strong gate (`tools/lint-style.sh`, `check_links`, `validate_skill`,
`check_versions`, `check_budgets`, `check_neutrality`, the script suite, `reconcile detect`), but
until now it only ran on demand (`npm run lint` / CI). That leaves the anti-vibe guarantee resting on
the agent *choosing* to run it - which is the one thing you cannot rely on. A 2026-07-04 session
proved the point: it filed several CRs, never ran the gate locally, and pushed commits that broke the
style, neutrality, and budget guards. The enforcement existed; the invocation did not.

This CR closes the last mile: a **tracked `.githooks/pre-commit`** that runs the whole
npm-independent gate on every commit, so a breaking change is refused at the moment it is made rather
than discovered later in CI. Two design choices matter:

1. **Detailed, self-diagnosing failures (per CR0025 / CR0132).** For each failing guard the hook
   prints *what it enforces*, the *full violation output* (file:line and the offending text), and
   *how to fix it*. Drift findings print each item with its own `fix` string. A blocked commit tells
   you exactly what to do, never a bare "FAIL".
2. **npm-independent + fast.** Every check except markdownlint is stdlib Python or bash, so the hook
   works without Node. The script unit tests run only when the commit touches `scripts/` or `tools/`,
   so a docs-only commit stays fast. `git commit --no-verify` remains the documented emergency
   bypass.

Enablement is one command per clone (`bash tools/enable-hooks.sh`, which sets `core.hooksPath` to the
tracked `.githooks/`), documented in AGENTS.md, CONTRIBUTING.md, and the README.

## Acceptance Criteria

- [x] `.githooks/pre-commit` runs style, links, skill-spec, versions, budgets, neutrality, drift, and
      (when `scripts/`/`tools/` are touched) the script suite; exits non-zero on any failure
- [x] every failure prints what the guard enforces, the full violation detail, and a fix hint; drift
      items print their per-finding `fix`
- [x] the hook is npm-independent (only optional markdownlint needs Node) and skips the script suite
      for commits that do not touch code
- [x] `tools/enable-hooks.sh` sets `core.hooksPath` to `.githooks`; documented in AGENTS.md +
      CONTRIBUTING.md + README.md, with `--no-verify` named as the emergency bypass
- [x] the hook passes clean on the current tree and blocks a seeded violation (verified: an injected
      em-dash is caught with file:line + fix)
- [x] `CHANGELOG.md` `[Unreleased]` entry ([[LL0004]])

## Out of Scope

- A server-side / CI-required check (CI already runs the same guards; this is the local first line).
- Auto-fixing violations (the hook explains and blocks; the author fixes, except `reconcile apply`
  for mechanical drift, which the hint names).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
| 2026-07-04 | claude | Implemented + wired + documented; verified clean-pass and detailed-block; Complete |
