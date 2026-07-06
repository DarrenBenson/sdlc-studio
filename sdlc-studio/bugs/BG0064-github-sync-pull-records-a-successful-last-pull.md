# BG0064: github_sync pull records a successful last_pull even when every gh call failed

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

`gh_issue_list` returns `[]` on a non-zero `gh` exit (a swallowed failure), and `cmd_pull`
then unconditionally stamps `state["last_pull"]` and exits 0 - converting a transient network
or auth failure into a clean-looking, state-advancing "nothing to pull" run.

## Evidence

- `.claude/skills/sdlc-studio/scripts/github_sync.py:84-96` - `gh_issue_list` prints to
  stderr and returns `[]` on non-zero exit (failure indistinguishable from empty).
- `github_sync.py:447-450` - `cmd_pull` unconditionally sets `state["last_pull"] = now_iso()`
  and saves, then prints "pull: issues_needing_ingest=0" and exits 0.

## Impact

The sync-state file asserts a pull happened at time T that never did. A cascading workflow
keyed on `last_pull`/timestamps is misled - a swallowed failure recorded as success
(LL0009: silent misleading failure outranks loud failure of the same scope).

## Steps to Reproduce

1. Run `github_sync.py pull` with `gh` unauthenticated (list call exits non-zero).
2. Observe the stderr line but exit 0, "issues_needing_ingest=0", and an advanced
   `last_pull` timestamp in the state file.

## Proposed Fix

Have `gh_issue_list` distinguish failure from empty (return `None` or raise), and in
`cmd_pull` skip the state stamp and exit non-zero when any list call failed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 architecture leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
