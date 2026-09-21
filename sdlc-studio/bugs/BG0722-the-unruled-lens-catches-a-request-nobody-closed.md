# BG0722: the unruled lens catches a request nobody closed, not the request everybody abandoned - the dominant accumulation path is still unguarded

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py
> **Verification depth:** functional
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

- [ ] **AC1: a request whose children have not moved is reported, however recently the request itself was touched.**
  - **Given** an In Progress request edited today whose open children have not changed in six months
  - **When** the lens runs
  - **Then** it is reported as abandoned - the request's own date says only that somebody wrote on it, and the accumulation path this guard exists to catch is work that started and stopped
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_a_request_edited_today_with_frozen_children_is_reported
- [ ] **AC2: the sweep's own audit ruling does not reset the clock.**
  - **Given** the same request, with a dated audit ruling appended to it by a previous sweep
  - **When** the lens runs again
  - **Then** it is still reported - a guard that its own remedy silences goes blind exactly once it has been used, which is how `stale` was lost
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_an_audit_ruling_does_not_silence_the_lens
- [ ] **AC3: a request whose children ARE moving is not reported.**
  - **Given** an In Progress request with an open child changed this week
  - **When** the lens runs
  - **Then** it is absent - the discriminating half, and the one the shipped lens fails in the opposite direction by reporting nothing at all
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_a_request_with_moving_children_is_not_reported
- [ ] **AC4: the existing `unruled` finding is not replaced by this one.**
  - **Given** a backlog holding both an In Progress request with no unresolved child and an abandoned one
  - **When** the lenses run
  - **Then** both are reported, each under its own lens - they are complementary, finished-but-never-closed against started-and-left, and collapsing them would re-lose whichever the survivor does not catch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_both_lenses_report_their_own_case
- [ ] **AC5: the lens reports a non-zero count against THIS repository's backlog.**
  - **Given** the corpus as it stands, where the shipped lens reports zero against 37 In Progress requests
  - **When** the new lens runs over it
  - **Then** it finds at least one - a detector proved only on a fixture is the inert-mechanism class this repo has paid for repeatedly
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_the_lens_is_not_inert_against_the_real_corpus

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `backlog_triage.py`, judge the request by its own last-edited date rather than by its children's - the shipped behaviour | frozen children are reported |
| AC2 | in `backlog_triage.py`, include the sweep's own dated audit rulings when computing a child's last movement | an audit ruling does not silence it |
| AC3 | in `backlog_triage.py`, report every In Progress request without testing whether its children moved | a moving request is not reported |
| AC4 | in `backlog_triage.py`, fold the abandoned case into the existing `unruled` lens so one finding kind covers both | both lenses report their own case |
| AC5 | in `backlog_triage.py`, narrow the child scan to direct children of a single type, which is what makes the shipped lens report zero on this corpus | the lens is not inert |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
