# CR-0181: Route github_sync and verify_ac through the shared discovery layer; unify the root-flag grammar

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0018](../epics/EP0018-tooling-hardening-and-review-debt.md)
> **Priority:** Medium
> **Type:** Improvement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

`github_sync.py` forks its own artefact-discovery layer (duplicate type table, case-sensitive
glob, cwd-relative paths, no `--root`), and `verify_ac.py` repeats the case-sensitive glob and
spells its root flag `--repo-root` where every sibling uses `--root`. Both should route
discovery through `sdlc_md.artifact_files`/`ARTIFACT_TYPES` and share one root-flag grammar.

## Motivation

A repo using the tolerated lowercase filename convention (`cr0001.md`) gets partial sync and
partial verification with no error - the exact defect `lib/sdlc_md.py:451-453` documents and
fixed centrally. `github_sync` only works when invoked from the repo root. The inconsistent
`--root` / `--repo-root` / no-root grammar breaks the fixed script contract the TRD documents
(§5) and trips up agents scripting the tools.

## Scope

**In scope**

- `github_sync.py`: replace `TYPE_DIRS` (github_sync.py:54-58) with `sdlc_md.ARTIFACT_TYPES`;
  route discovery through `sdlc_md.artifact_files` (fixes the case-sensitive glob at
  github_sync.py:229); add `--root`, resolving `STATE_PATH` (github_sync.py:60) against it.
- `verify_ac.py`: route `walk_stories` (verify_ac.py:516-521) through
  `sdlc_md.artifact_files("story", ...)`; add `--root` as an alias for `--repo-root`
  (verify_ac.py:886).
- Same fix for `status.py:141` (`walk_glob(... "RV*.md")`) if it shares the case-sensitive
  pattern.

**Out of scope**

- Changing the sync body-update contract (a separate question flagged as an open item, not a
  finding).
- The create-path/reconcile-path master-table convergence (BG0066 tracks the append side).

## Acceptance Criteria

- [ ] A fixture repo with lowercase-named artefacts syncs and verifies fully (test both).
- [ ] `github_sync.py --root <dir>` works from outside the repo root; `STATE_PATH` resolves
      against `--root`.
- [ ] `verify_ac.py --root` is accepted (alias of `--repo-root`); the grammar is consistent
      across scripts.
- [ ] No duplicate `TYPE_DIRS`; discovery flows through the shared layer.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| BG0063, BG0064 | Same file (github_sync); natural to fix in one pass |
| CR0187 | Themed code-quality debt; this is the larger shared-layer-bypass item pulled out separately |

## Risk

Low. Behaviour-preserving for the shipped uppercase convention; the change surfaces
previously-missed lowercase artefacts, which is the intent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted from RV0006 architecture leg |
