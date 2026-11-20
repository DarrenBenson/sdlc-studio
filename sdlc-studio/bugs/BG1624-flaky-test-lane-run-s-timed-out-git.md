# BG1624: Flaky: test_lane_run's timed-out git add test can find index.lock left behind on the gate host

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, changelog.d/BG1624.md
> **Evidence:** run eighteen, 2026-11-19: push of 294770b0 refused, devserver1 boundary-suite-last.log lines 221-240; 1 failed, 9292 passed
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T17:25:59Z

## Summary

LaneTimeoutTermsFirstTests::`test_a_timed_out_git_add_loop_leaves_no_index_lock` failed once at the push boundary on devserver1 (commit 294770b0): 'a killed git add left index.lock' at `test_lane_run.py`:701, after the loop had staged its file. It passes 5 of 5 locally, passed at every earlier push, and run eighteen changed nothing on lane run's kill path, so the test races under the host's load: with --timeout 1, a git add caught by the escalation after SIGTERM's grace can leave its lock.

## Steps to Reproduce

Run .claude/skills/sdlc-studio/scripts/tests/`test_lane_run.py`::LaneTimeoutTermsFirstTests under the push boundary's parallel full suite on a loaded host: it fails intermittently on the index.lock assertion.

## Proposed Fix

Make the test independent of the grace window (wait for the loop's git add to finish a write before the timeout, or give the lane a timeout and grace the host can meet), or make lane run remove a lock its own killed git left before it reads the staged set; keep the SIGKILL-first mutant killed.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: LaneTimeoutTermsFirstTests::`test_a_timed_out_git_add_loop_leaves_no_index_lock` failed once at the push boundary on devserver1 (commit 294770b0): 'a killed...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run .claude/skills/sdlc-studio/scripts/tests/`test_lane_run.py`::LaneTimeoutTermsFirstTests under the push boundary's parallel full suite on a loaded host: it...
- [ ] **AC3** The proposed fix lands, pinned by a test: Make the test independent of the grace window (wait for the loop's git add to finish a write before the timeout, or give the lane a timeout and grace the host...

- Recurred in run twenty (RUN-01M7VNR0, 2026-11-20): the commit lane of `lane land` for the US1056/US1057/US1322 repair failed on `LaneTimeoutTermsFirstTests::test_a_timed_out_git_add_loop_leaves_no_index_lock` (index.lock left) with 4406 other tests green, locally under load during a 1017s selection; the landing was re-run with `--resume`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
