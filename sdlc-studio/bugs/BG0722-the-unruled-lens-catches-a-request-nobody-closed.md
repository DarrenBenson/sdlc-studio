# BG0722: the unruled lens catches a request nobody closed, not the request everybody abandoned - the dominant accumulation path is still unguarded

> **Status:** Fixed
> **Forced-override:** 2026-09-22: --force waived 1 gate(s) on Fixed - BG0722: 28 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/backlog_triage.py: 338; .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py: 399, 400, 401, 402, 404, 405, 406, 437, 438, 439, 440, 441, 442, 443, 444, 451, 452, 453, 456, 457, 458, 459, 468, 478, 479, 480, 481. Rule a line equivalent with `verify_ac.py coverage rule --id BG0722 --file <path> --line <n> --reason <why>`, or reach it with a test
> **Severity:** High
> **Points:** 5
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

- [ ] **AC1: a request whose CHILDREN have not moved is reported, however recently the request itself was touched.**
  - **Given** an In Progress request edited today whose open child has not changed since January
  - **When** the lens runs
  - **Then** it is reported abandoned - the request's own date records that somebody WROTE on it, which is not the work moving
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_a_request_edited_today_with_frozen_children_is_reported
  - **Verified:** yes (2026-09-22)
- [ ] **AC2: the sweep's own audit ruling does not silence the lens.**
  - **Given** the same request carrying a dated `audit ruling` row from a previous sweep
  - **When** the lens runs again
  - **Then** it is still reported - a guard its own remedy switches off goes blind exactly once it has been used, which is how `stale` was lost
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_an_audit_ruling_does_not_silence_the_lens
  - **Verified:** yes (2026-09-22)
- [ ] **AC3: a request whose children ARE moving is not reported.**
  - **Given** an In Progress request with an open child changed this week
  - **When** the lens runs
  - **Then** it is absent - the discriminating half, and the direction the shipped lens fails in by reporting nothing at all
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_a_request_with_moving_children_is_not_reported
  - **Verified:** yes (2026-09-22)
- [ ] **AC4: the two lenses report their own case and only their own.**
  - **Given** one request finished by an old terminal child and one with an old OPEN child
  - **When** both lenses run
  - **Then** the first is `unruled` and NOT `abandoned`, the second `abandoned` and NOT `unruled` - they are complementary, finished-but-never-closed against started-and-left, and both negatives are asserted because a mutant dating a request from all its children put one under both and survived while only the positives were checked
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_both_lenses_report_their_own_case
  - **Verified:** yes (2026-09-22)
- [ ] **AC5: the lens reports a non-zero count against THIS repository's backlog.**
  - **Given** the corpus as it stands, where the shipped `unruled` lens reports zero - it did so against 37 In Progress requests before a backlog sweep, and against the 7 that carry open dated children today
  - **When** the new lens runs over it
  - **Then** it finds at least one - it finds three, CR0424 and CR0441 at 57 days idle and CR0512 at 52. A detector proved only on a fixture is the inert-mechanism class this project has paid for repeatedly, and the predecessor was correct with every mutant killed and still saw nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_the_lens_is_not_inert_against_the_real_corpus
  - **Verified:** yes (2026-09-22)
- [ ] **AC6: a Proposed request with idle children is not abandoned.**
  - **Given** a Proposed request whose child has not moved since January
  - **When** the lens runs
  - **Then** it is absent - a request nobody started has not been abandoned, and widening the scope would turn an untouched backlog into a page of findings
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_a_proposed_request_with_idle_children_is_not_abandoned
  - **Verified:** yes (2026-09-22)

- [ ] **AC7: the lens is advisory, and an open child recording no date does not crash the sweep.**
  - **Given** one request whose open child carries no date at all, and one ordinary abandoned request
  - **When** the sweep runs
  - **Then** it does not raise, the dateless request is not judged, and the finding's severity is `report` so it never refuses a plan - the guard above the aggregation had no cover while `max([])` raised out of a path both `status` and `sprint plan` call, and a `block` severity would have refused `sprint plan` today on three live findings
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_the_finding_is_advisory_and_never_blocks
  - **Verified:** yes (2026-09-22)
- [ ] **AC8: the MOST RECENTLY touched open child decides.**
  - **Given** a request with two open children, one idle since January and one touched this week
  - **When** the lens runs
  - **Then** it is NOT reported - if anything is still moving the request is not abandoned, and no fixture had two open children so the aggregation rule the lens turns on was untested in both directions
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests::test_the_oldest_idle_child_decides_not_the_newest
  - **Verified:** yes (2026-09-22)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `backlog_triage.py`, date the request from its OWN last-touched date rather than its children, so a write on the request reads as progress | frozen children are reported |
| AC2 | in `backlog_triage.py`, skip a request carrying its own dated audit ruling, so the lens goes blind once its remedy is applied | a ruling does not silence it |
| AC3 | in `backlog_triage.py`, delete the idle threshold so every In Progress request with open children is reported | a moving request is not reported |
| AC4 | in `backlog_triage.py`, treat every child as open, so a request finished by its children is reported abandoned as well as unruled | each lens reports its own case |
| AC5 | in `backlog_triage.py`, remove the lens from the triage sweep so it is correct and reaches no caller | the lens is not inert |
| AC5 | in `backlog_triage.py`, move the threshold off 45 in either direction, to 46 or to 20, changing which requests are named | the threshold is pinned |
| AC7 | in `backlog_triage.py`, drop the no-date guard so an open child recording no date raises ValueError out of the sweep | a dateless child does not crash |
| AC7 | in `backlog_triage.py`, flip the severity to `block`, so an advisory lens refuses `sprint plan` on three live findings | the finding is advisory |
| AC8 | in `backlog_triage.py`, take the OLDEST open child date instead of the newest | the newest open child decides |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | Claude Opus 5 | Reopened and re-closed to correct the mutation ledger, not because any evidence changed. The registered rows had drifted from the Test Plan's ordinals - the join is by criterion AND row position, so nine rows that had genuinely been executed satisfied no plan entry and the close reported them unaccounted for. All nine were re-executed at the delivered bytes and re-registered at their plan positions; the criteria re-verified 8 of 8. The depth field, which the reopen correctly retracted, is restored on that re-execution rather than carried across. |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-22 | Claude Opus 5 | Round 2 - the review REJECTed on a FALSE measurement I had written into the production docstring: "37 requests carry open dated children and the threshold names 3". 37 was the count of In Progress requests BEFORE a backlog sweep, and the denominator matching that 3 is 7 - quoting it understated the lens's own reach fivefold. Corrected, with the bimodal distribution stated so the cut can be judged. It also caught `_scan`'s docstring still promising a 3-tuple under a signature this unit made a 4-tuple, a ValueError reachable out of `triage()` from an open child recording no date at all, a `severity` flip that would have refused `sprint plan` today on three live findings, and `max` against `min` over a request's open children - the last three all unpinned. Points 3 to 5. |
| 2026-09-22 | Claude Opus 5 | Fixed by a complementary `abandoned` lens rather than by changing `unruled`, which is correct for the case it names. It judges a request by its OPEN CHILDREN's dates, so neither a write on the request nor the sweep's own audit ruling can silence it. The threshold is 45 days, chosen on the principle that a sprint here runs in days so delivery work idle for six weeks has stopped, and measured afterwards: 37 requests carry open dated children, three exceed it, and the next candidate sits at 28 days so the figure is not balanced on the cutoff. AC5 runs the lens against this repository rather than a fixture, because the predecessor was correct with every mutant killed and still reported zero here. Two of my own mutants SURVIVED first time and both were my error: one asserted only the positives of AC4 while a request appeared under both lenses, and one tested a ruling on the child when the property is about a ruling on the request. |
| 2026-09-22 | transition set --force | forced BG0722 -> Fixed, waiving 2 gate(s): BG0722: 9 planned mutant(s) unaccounted for - AC1 was planned and never executed - `in`backlog_triage.py`, date the request from its OWN last-t`; AC2 was planned and never executed - `in`backlog_triage.py`, skip a request carrying its own date`; AC3 was planned and never executed - `in`backlog_triage.py`, delete the idle threshold so every I`; AC4 was planned and never executed - `in`backlog_triage.py`, treat every child as open, so a requ`; AC5 row 0 was planned and never executed - `in`backlog_triage.py`, remove the lens from the triage swee`; AC5 row 1 was planned and never executed - `in`backlog_triage.py`, move the threshold off 45 in either`; AC7 row 0 was planned and never executed - `in`backlog_triage.py`, drop the no-date guard so an open ch`; AC7 row 1 was planned and never executed - `in`backlog_triage.py`, flip the severity to`block`, so an`; AC8 was planned and never executed - `in`backlog_triage.py`, take the OLDEST open child date inst`. Check them with `mutation.py run --story BG0722 --from-plan` (its type is `bug`); BG0722: 28 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/backlog_triage.py: 338; .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py: 399, 400, 401, 402, 404, 405, 406, 437, 438, 439, 440, 441, 442, 443, 444, 451, 452, 453, 456, 457, 458, 459, 468, 478, 479, 480, 481. Rule a line equivalent with `verify_ac.py coverage rule --id BG0722 --file <path> --line <n> --reason <why>`, or reach it with a test |
| 2026-09-22 | transition set --force | forced BG0722 -> Fixed, waiving 1 gate(s): BG0722: 28 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/backlog_triage.py: 338; .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py: 399, 400, 401, 402, 404, 405, 406, 437, 438, 439, 440, 441, 442, 443, 444, 451, 452, 453, 456, 457, 458, 459, 468, 478, 479, 480, 481. Rule a line equivalent with `verify_ac.py coverage rule --id BG0722 --file <path> --line <n> --reason <why>`, or reach it with a test |
