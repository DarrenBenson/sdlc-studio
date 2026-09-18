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

- [ ] **AC1** The behaviour described is corrected: `_open_findings` dates a finding by the LAST WORD of its `Raised-in-batch` stamp.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Measured on RUN-01M2SPNS, which filed exactly two findings (BG0713, BG0714): None of BG0679-BG0690 was raised by this run.
- [ ] **AC3** The proposed fix lands, pinned by a test: Read the DATE from the stamp rather than its last token: parse an ISO timestamp out of it and treat a stamp carrying none as undatable.

## Impact

The close cannot complete on any project with findings raised outside a delivery batch, which is the ordinary case for a backlog sweep or an audit. The retro is asked to rule findings the run never saw, and a run that ruled them would be recording 81 judgements nobody made. It refused RUN-01M2SPNS's PREPARE with 81 findings against a run that filed two.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Filed |
