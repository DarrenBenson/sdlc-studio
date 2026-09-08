# BG0638: five sprint-checklist rows state a conclusion they never established, and _ck_known_issues FAILS OPEN where its own sibling reports the same blindness as UNANSWERED

> **Status:** Superseded
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

- [ ] **AC1** Given a run whose planned set names a unit the retro's Batch line omits, when the sprint checklist renders, then `not-delivered` reports the shortfall rather than 'none - every planned unit was delivered', so it agrees with `planned-vs-delivered` on the same page instead of contradicting it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistHonestyTests::test_not_delivered_reports_the_shortfall_planned_versus_delivered_sees
  - **Verified:** no
- [ ] **AC2** Given a run record with no `started_at`, when the checklist renders, then `known-issues` is UNANSWERED naming the unreadable half rather than ANSWERED 'none carried' - an absence of evidence is not evidence of none, which is the distinction the impediments row on the same page already draws.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistHonestyTests::test_known_issues_is_unanswered_when_the_run_carries_no_start_time
  - **Verified:** no

## Impact

These rows are the close's own account of what a run committed to and what it left owed. A row that asserts a conclusion it never established is worse than a missing row, because the close reads as complete. `_ck_known_issues` failing open is the sharpest: it is the compulsory item that decides whether a sprint leaves an open finding, and it answers 'none carried' when it cannot see.

## Test Plan

| AC | The edit the test must fail on | Criterion |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint_report.py, return the 'none - every planned unit was delivered' sentence whenever the delivered set is non-empty, ignoring the planned set it is compared against | Given a run whose planned set names a unit the retro's Batch line omits, when the sprint checklist renders, then `not-delivered` reports the shortfall rather than 'none - every planned unit was delivered', so it agrees with `planned-vs-delivered` on the same page instead of contradicting it. |
| AC2 | in sprint_report.py, treat a missing `started_at` as an empty finding set rather than as unreadable, so the row renders ANSWERED | Given a run record with no `started_at`, when the checklist renders, then `known-issues` is UNANSWERED naming the unreadable half rather than ANSWERED 'none carried' - an absence of evidence is not evidence of none, which is the distinction the impediments row on the same page already draws. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-02 | sdlc-studio | Filed |
| 2026-09-08 | Claude Fable 5.1 | SUPERSEDED by BG0458, delivered in 80281c2f on 2026-07-31 - a month before this was filed on 2026-09-02. Both halves ship: `_ck_not_delivered` reads the planned set and its comment restates AC1 verbatim (`sprint_report.py:1721-1738`), and `_ck_known_issues` opens BLINDNESS FIRST, returning UNANSWERED `unreadable` naming the missing start time, which is AC2 verbatim (`sprint_report.py:2001-2014`). Found by the engineering seat at the goal review by executing both probes, before any code was written for it. No work is owed; the finding was a re-filing of a closed defect |
