# BG0799: A first sprint's report hands over, as known issues, the epic drift its own close settles, split into one row per line of reconcile's output

> **Status:** Open
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py, changelog.d/BG0799.md
> **Severity:** Medium
> **Points:** 2

## Summary

On a fresh rc.1 project whose only epic's one story reached Done, `sprint.py close` recorded `epic-status-stale` at its reconcile step [9/10], then its own tail (`apply-signoff: derived EP-... terminal`) set the epic Done, and the report filed by the same close handed over five rows for that one item: the drift line, reconcile's `scope=all drift_items=1 by_kind=...` summary, its `Guidance:` header, the guidance bullet, and the report-hold row. `close_known_issues_from` splits a failed step's detail per line, and the reconcile step runs before the tail that settles the epic. Every project whose epic completes in a sprint meets this on its first report: '6 close gap(s)' for a clean run.

## Steps to Reproduce

init run; artifact new epic + one story with a green Verify; sprint plan --write; `verify_ac` run; critic brief/record APPROVE; transition set <story> Done; commit; sprint close; fill the retro; sprint close --retro RETRO-0001 --goal-verdict achieved --note ...: the report's Known issues table carries 5 rows for one drift item the close resolved.

## Proposed Fix

Settle close-owned derivations (parent epics of this run's units) before the reconcile step reads drift, or read drift after the tail; and carry one known issue per drift item from reconcile's structured detection, never per stdout line.

## Acceptance Criteria

- [ ] Given a fresh `init` project whose only epic's single story reaches Done in the run, when `sprint.py close --retro <R> --goal-verdict achieved` files the report, then the epic reads Done and the report's Known issues table carries no `epic-status-stale` row. Fails on: HEAD (five rows for one item the same close resolved, measured on a fresh rc.1 project 2026-09-27); suppressing every reconcile issue, which AC2 catches
- [ ] Given index drift the close does not settle (a story's index row hand-edited to a stale status), when the close runs, then the report carries exactly one known-issue row per drift item, naming the id and the kind, and no row for reconcile's `scope=` summary or `Guidance:` lines. Fails on: splitting the reconcile step's stdout per line (HEAD)

## Notes

First-week (Maya's first report). Found by the QA seat walking the lean loop on a fresh rc.1 project. Ratchet (LC-008): adds no check. Related to US0951 (a clean run's report hands over no false known issue), which this reopens on a path its fixture did not reach (an epic that completes).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0799) |
