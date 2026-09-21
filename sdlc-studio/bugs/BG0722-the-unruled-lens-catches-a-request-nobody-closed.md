# BG0722: the unruled lens catches a request nobody closed, not the request everybody abandoned - the dominant accumulation path is still unguarded

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0848 delivers CR0591 AC4: a discovery request that is In Progress, has NO UNRESOLVED CHILD, and carries no dated audit ruling is reported. That is a real accumulation path and the lens works - three mutants applied and killed. But it is not the path RUN-01M306PY is clearing. Run against the real backlog immediately after delivery it reports ZERO, because all 37 In-Progress requests have at least one child that is still open. The state that actually accumulated here is a request started, worked partway, and left: children at every depth, nothing moving for months, status In Progress because nothing makes anybody say otherwise. The run's goal says the state that let them accumulate CANNOT REBUILD, and after this sweep it still can - every request ruled `still wanted, correctly in progress` keeps its open children and is invisible to both this lens and the existing `stale` lens. Worse, the sweep makes the stale lens permanently blind to them: `_last_date` reads the most recent revision row, and every one of the 38 is about to get a dated audit ruling, so none will ever read as stale again.

## Steps to Reproduce

1. Take a discovery request that is In Progress with one Done child and one Draft child, untouched for six months. 2. Run `backlog_triage.py check`. 3. Neither the `unruled` lens (it has an unresolved child) nor the `stale` lens (its revision history was touched) reports it. Observed on the real backlog: 37 such requests, 0 findings.

## Proposed Fix

Judge a request by whether its CHILDREN have moved, not by its own last-edited date or by whether they all finished. A request that is In Progress and none of whose open children has changed in N days is abandoned, whatever its own revision history says - and the audit ruling this sweep adds must not reset that clock, which is the trap the current `stale` lens falls into. Note the interaction with US0848: the two lenses are complementary, not alternatives - one catches finished-but-never-closed, the other catches started-and-left - and the run's goal needs both. Add a criterion for a request whose own date is today and whose children have not moved in six months.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0848 delivers CR0591 AC4: a discovery request that is In Progress, has NO UNRESOLVED CHILD, and carries no dated audit ruling is reported.
- [ ] **AC2** The proposed fix lands, pinned by a test: Judge a request by whether its CHILDREN have moved, not by its own last-edited date or by whether they all finished.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
