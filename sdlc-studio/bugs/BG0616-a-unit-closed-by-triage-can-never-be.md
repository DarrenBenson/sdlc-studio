# BG0616: a unit CLOSED by triage can never be covered by a retro, so it owes a close-down for ever and the advisory can only be cleared by lying

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Evidence:** `close_owed.py detect` on 2026-08-26 reports BG0599 and BG0602 owed. Both are at Closed. RETRO0109 names BG0599 four times and neither in its Batch line. Coverage mechanism quoted from source at close_owed.py:167-176, and the epic precedent at close_owed.py:549-553, per D0151.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`close_owed.covered_ids` (`close_owed.py`:167-176) builds the covered set from each retro's `Batch` field and nothing else. A unit closed by pre-code triage - premise did not reproduce at HEAD, closed WON'T FIX or Closed rather than built - is by definition NOT in the run's batch, and putting it there would misstate what the run delivered. So it is uncovered permanently and no future close can clear it. Measured 2026-08-26: `close_owed.py detect` reports BG0599 and BG0602 owed, while RETRO0109 names BG0599 FOUR times - in its Blocked and deferred section and in its findings table as `fixed-in: BG0599, BG0602 and BG0463 closed with their source lines recorded` - and names neither in its Batch line, correctly. The retro that accounts for them exists and the checker cannot see it. `owed`'s own docstring already records this exact failure mode for EPICS at `close_owed.py`:549-553: an epic is never named in a Batch, so requiring it manufactured debt no further close could clear, and epics were given an inheritance rule. Triage-closures have the same shape and no rule.

## Steps to Reproduce

1. Open a run whose pre-code goal review finds a unit's premise does not reproduce. 2. Close that unit by triage rather than building it, and account for it by name in the retro's Blocked/deferred section. 3. Close the run. 4. `close_owed.py detect` reports the unit owed, and every subsequent `hint` and `status` repeats the advisory. Measured on BG0599 and BG0602, closed before RUN-01M0WCCG and named in RETRO0109.

## Proposed Fix

Give a triage-closure the same treatment epics already have. The cleanest source is the retro itself: count a unit COVERED when a retro names it in the dispositioned-findings table or the Blocked/deferred section, not only in `Batch` - the close already refuses a retro whose findings are undispositioned, so that section is gated content rather than free prose. Failing that, let the close record a triage-closure set beside its batch. What must NOT happen is the only currently available remedy: adding a non-delivered unit to a Batch line, which would make the retro's own delivered count false and would be read by `retro accuracy` as delivery.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `close_owed.covered_ids` (`close_owed.py`:167-176) builds the covered set from each retro's `Batch` field and nothing else.
- [ ] **AC2** The proposed fix lands, pinned by a test: Give a triage-closure the same treatment epics already have.

## Impact

An advisory that cannot be cleared by correct behaviour is one operators learn to ignore, and it sits on `hint` and `status` - the two commands every session runs first, and the same surface BG0615 was found on. It also punishes exactly the behaviour this project wants: a pre-code goal review that kills a unit before any code is written is the cheapest possible outcome, and it is the one that manufactures permanent debt.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
