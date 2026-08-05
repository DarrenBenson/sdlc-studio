# BG0524: warning-ratchet reports a stale baseline as clean and exits 0, contradicting US0480 AC4 and its own docstring

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** Engineering review seat, RUN-01KZ79C1 boundary, through the shipped CLI on an isolated fixture.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0480 AC4 requires four untrustworthy-baseline states, each non-zero, and forbids reporting clean on a reference the ratchet could not establish. It names `stale` as one of the four. `validate.py`'s own docstring for `read_warning_baseline` says the same: `Four untrustworthy states, each distinct and each non-zero`.

The shipped behaviour differs. On a baseline recording an instance no artefact still carries, `warning-ratchet` exits 0 and prints `warning-ratchet: clean. 1 recorded instance(s), none new.` The stale entries are listed below that line, but the headline says clean and the exit code agrees.

AC2 asks for the opposite: a repaired instance must be reported as removable WITHOUT holding the gate, because refusing the commit that repaired something teaches an author to stop repairing. The code follows AC2. So AC2 and AC4 contradict each other, and one of them has to change - this is a specification defect as much as a code one.

## Steps to Reproduce

1. Stamp a baseline, then delete the artefact carrying one of its instances.
2. `validate.py warning-ratchet` - redirect, do not pipe.
3. Exit 0, headline `clean`, stale entries listed underneath.

## Proposed Fix

Decide which criterion is right and make the other follow. The AC2 behaviour is the defensible one - a repaired instance is good news and must not refuse the commit that repaired it - so AC4's enumeration should drop `stale` from the non-zero set, and the docstring with it. If instead stale should refuse, AC2's rationale needs answering, not overriding. Either way the headline must stop saying `clean` while listing entries the ratchet could not verify.

## Acceptance Criteria

- [ ] The behaviour described is corrected: US0480 AC4 requires four untrustworthy-baseline states, each non-zero, and forbids reporting clean on a reference the ratchet could not establish.
- [ ] The proposed fix lands, pinned by a test: Decide which criterion is right and make the other follow.

## Impact

A criterion is marked Verified against behaviour the code does not have, and the module docstring states a rule the module does not follow - so the next reader trusts a four-state guarantee that is three.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
