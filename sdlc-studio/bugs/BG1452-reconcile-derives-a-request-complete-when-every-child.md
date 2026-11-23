# BG1452: reconcile derives a request Complete when every child of a partial refine resolves, though its unrefined criteria are undelivered

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_refine_partial.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/help/refine.md, changelog.d/BG1452.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:38:17Z

## Summary

CR0692 was refined in part (AC1 and AC2 into EP0308) and reconcile derived it Complete once US1155 and US1156 resolved, leaving AC3 and AC4 undelivered; the remainder had to be filed as CR0704. refine has no way to record that a request is decomposed in part.

## Steps to Reproduce

Refine a request's first two criteria into an epic, deliver it, then run `reconcile detect`: the request is request-derivable Complete.

## Proposed Fix

Let refine mark a request decomposed in part (naming the criteria left), and have reconcile not derive a terminal while any are left.

## Acceptance Criteria

- [ ] **AC1** Given a request refined in part, when all its children resolve, then reconcile does not derive it Complete and names the criteria still unrefined. Fails on: a derived Complete.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_partial.py::RefinePartialTests
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Affects widened before landing: transition._request_terminal_gate must read the new Unrefined record, or a hand-set Complete still closes a request refined in part, and help/refine.md must document --unrefined; found by the REF builder |
