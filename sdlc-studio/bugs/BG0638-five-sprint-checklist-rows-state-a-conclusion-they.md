# BG0638: five sprint-checklist rows state a conclusion they never established, and _ck_known_issues FAILS OPEN where its own sibling reports the same blindness as UNANSWERED

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

An adversarial review of US0570, US0571, US0575 and US0576 on 2026-07-31 found five checklist rows asserting conclusions their own computation cannot support. It was recorded as a REJECT and never answered; the units are Done and the findings are still live. `_ck_not_delivered`iterates the RETRO's Batch rather than the run's planned set, so a planned unit absent from the retro is reported nowhere while the row asserts 'none - every planned unit was delivered' and planned-vs-delivered on the same page reads 1/2.`held`is read from the append-only`deferred_units`with no pending check, and sprint decision resolve never removes from it, so a resolved-then-shipped unit renders held AND counted delivered.`_ck_known_issues`FAILS OPEN:`_open_findings`returns empty on a missing run record or absent`started_at`and`_carried_issues`swallows every exception, so a blind scan renders ANSWERED 'none carried' with an Open bug on disk and does not hold the close - while the sibling`_ck_impediments` distinguishes exactly that blindness as UNANSWERED on the very same page.

## Steps to Reproduce

1. Take a run whose planned set contains a unit the retro's Batch line omits.
2. `sprint.py report --id RETROxxxx`.
3. `not-delivered`reports 'none - every planned unit was delivered' while`planned-vs-delivered` on the same page reads a shortfall.
4. Remove the run record's `started_at`; `known-issues` renders ANSWERED 'none carried' with an Open bug on disk.

## Proposed Fix

Read the planned set from the run record rather than the retro's Batch line - the retro is the account, not the source. Give `held`a pending check and make decision resolve remove from`deferred_units`, or the append-only list means held is a claim nobody retracts. Make `_ck_known_issues`distinguish BLINDNESS from ABSENCE exactly as`_ck_impediments` already does on the same page: a scan that could not run reports UNANSWERED, never ANSWERED 'none carried'. The two rows disagreeing about the same condition is the tell.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: An adversarial review of US0570, US0571, US0575 and US0576 on 2026-07-31 found five checklist rows asserting conclusions their own computation cannot support.
- [ ] **AC2** The proposed fix lands, pinned by a test: Read the planned set from the run record rather than the retro's Batch line - the retro is the account, not the source.

## Impact

These rows are the close's own account of what a run committed to and what it left owed. A row that asserts a conclusion it never established is worse than a missing row, because the close reads as complete. `_ck_known_issues` failing open is the sharpest: it is the compulsory item that decides whether a sprint leaves an open finding, and it answers 'none carried' when it cannot see.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-02 | sdlc-studio | Filed |
