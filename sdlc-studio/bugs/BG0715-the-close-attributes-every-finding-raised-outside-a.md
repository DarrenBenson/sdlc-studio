# BG0715: the close attributes every finding raised outside a delivery batch to whichever run is open, because it dates them by the last word of a prose stamp

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_open_findings` dates a finding by the LAST WORD of its `Raised-in-batch` stamp. A finding raised outside a delivery batch carries the prose stamp `none open - raised outside a delivery batch`, whose last word is `batch` - and `'batch' < '2026-09-18T07:20:32Z'` is False, so it sorts as inside every run window. Every such finding in the project's history is therefore attributed to whichever run happens to be open, and the close's known-issues row demands a stop-ship ruling for all of them.

## Steps to Reproduce

Measured on RUN-01M2SPNS, which filed exactly two findings (BG0713, BG0714):

```text
close STOPPED at checklist [6/10]:
  known-issues: Known issues carried, each with its stop-ship ruling - 81 unruled
      UNRULED BG0679; UNRULED BG0680; ... BG0690 - an open finding nobody ruled on
```

None of BG0679-BG0690 was raised by this run. Each carries `> **Raised-in-batch:** none open - raised outside a delivery batch`.

The arithmetic, reproduced:

```python
stamp = 'none open - raised outside a delivery batch'
when = stamp.split()[-1]          # 'batch'
when < '2026-09-18T07:20:32Z'     # False - so the row is NOT skipped
```

`_open_findings` (`sprint_report.py)` comments that 'a stamp naming no batch still carries the moment it was raised' - but the no-batch stamp carries no moment at all, only prose. The guard `if not when` catches an EMPTY stamp and misses a prose one.

## Proposed Fix

Read the DATE from the stamp rather than its last token: parse an ISO timestamp out of it and treat a stamp carrying none as undatable. An undatable finding is then either excluded from the window (it cannot be shown to be this run's) or reported separately as undatable - never silently counted as inside. The `if not when` guard already draws the right distinction for an empty stamp; it needs to draw the same one for a stamp with no date in it.

## Acceptance Criteria

- [ ] **AC1: a prose `Raised-in-batch` stamp is not read as a date.**
  - **Given** a finding stamped `none open - raised outside a delivery batch`
  - **When** the report derives its open findings for a run
  - **Then** that finding is NOT attributed to the open run - the stamp carries no ISO timestamp, so it cannot place the finding inside any window
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_a_prose_stamp_is_not_read_as_a_date
- [ ] **AC2: an undatable finding is reported, never silently dropped.**
  - **Given** the same finding
  - **When** the report renders
  - **Then** it appears in a named undatable set with its id, because a finding excluded without trace is the same defect one direction over
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_an_undatable_finding_is_named_rather_than_dropped
- [ ] **AC3: a finding genuinely raised inside the run is still attributed to it.**
  - **Given** a finding whose stamp carries an ISO timestamp inside the run's window
  - **When** the report derives its open findings
  - **Then** it IS attributed to the run - the discriminating half, because a parser that attributed nothing would pass AC1 and AC2 together
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_a_dated_stamp_inside_the_window_is_still_attributed
- [ ] **AC4: an empty stamp and a prose stamp are treated alike.**
  - **Given** one finding with an empty `Raised-in-batch` value and one with the prose stamp
  - **When** both are derived
  - **Then** both land in the undatable set - the existing guard drew the distinction only for the empty case, which is how the prose case reached the date comparison at all
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_an_empty_stamp_and_a_prose_stamp_reach_the_same_verdict

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint_report.py`, restore `_open_findings` to take the stamp's last whitespace-separated token as its date, so `batch` sorts before any ISO timestamp - the shipped behaviour | a prose stamp is not a date |
| AC2 | in `sprint_report.py`, drop an undatable finding from the derivation instead of collecting it into the reported set | an undatable finding is named |
| AC3 | in `sprint_report.py`, widen the undatable test so any stamp is treated as unparseable, attributing nothing to the run | a dated stamp is still attributed |
| AC4 | in `sprint_report.py`, narrow the undatable guard back to an empty value only, so a prose stamp falls through to the date comparison | empty and prose agree |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Filed |
