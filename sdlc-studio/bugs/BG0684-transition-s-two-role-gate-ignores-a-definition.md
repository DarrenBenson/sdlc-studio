# BG0684: transition's two-role gate ignores a Definition of Done that stands the review.two-role tag down

> **Status:** Superseded
> **Closes with:** US0916 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** US0626 round-4 QA plan review, 2026-09-15, probed at HEAD.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_two_role_gate` sets the cutoff to None for a DoD stand-down only after the `two_role_applies_to` check has returned, and never reads it again, so the stand-down has no effect: with a DoD lacking review.two-role the gate still refuses and names the reviewer-of-record sign-off, while conformance.py and `sprint._awaits_signoff` both honour it.

## Steps to Reproduce

1. A story Definition of Done without the review.two-role tag, `review.two_role_after` set, a unit past it.
2. `transition.py set --id <unit> --status Done` refuses naming the sign-off; `_awaits_signoff` returns False for the same unit.

## Proposed Fix

Apply the stand-down before the applies-to check returns, so the three readers agree; pin with the DoD fixture.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_two_role_gate` sets the cutoff to None for a DoD stand-down only after the `two_role_applies_to` check has returned, and never reads it again, so the...
- [ ] **AC2** The proposed fix lands, pinned by a test: Apply the stand-down before the applies-to check returns, so the three readers agree; pin with the DoD fixture.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0916 ships - planning: SUPERSEDED - two-role gate: per-unit two-role sign-off deleted in batch 2; superseded only once US0916 ships (D0264) |
| 2026-09-25 | sdlc-studio BG0772 | Superseded under D0264: its closing story US0916 is Done (BG0772) |
