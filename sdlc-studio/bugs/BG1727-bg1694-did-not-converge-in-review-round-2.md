# BG1727: BG1694 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_commit_timeout_group.py, tools/tests/test_test_census.py, changelog.d/BG1694.md
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T13:48:20Z

## Summary

BG1694 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the stand-in clock moves only inside its `sleep`, so a wait that polls `monotonic()` without sleeping never reaches its bound or the clock's limit and hangs the case: with `time.sleep(0.01)` dropped from `_wait_for` (test\_kill\_grace\_interrupt.py:57) or from `_pid` (test\_lane\_land\_commit\_timeout\_group.py:121), a bounded busy wait the wall clock would end at 0.2 s, `test_child_gives_up_at_its_bound` and `test_pid_gives_up_at_its_bound` each hung until a 60 s wall bound killed them, and no pytest-timeout is installed to end such a hang in the gate. That falsifies the round's own claim that "a loop that never gives up ends the case instead of hanging it" in both `_Clock` docstrings (test\_kill\_grace\_interrupt.py:68-72, test\_lane\_land\_commit\_timeout\_group.py:86-90) and in both `test_the_clock_ends_a_wait_that_never_gives_up` cases, which pin only a loop that keeps sleeping. A `monotonic()` that also moves the clock on and enforces the limit, with a case pinning it, or a claim narrowed to a wait that keeps sleeping, closes it; [pre-existing] AC4's Verify, `tools/tests/test_test_census.py::WallClockCensusTests`, ran 198 s and 207 s here at load average 12, past verify\_ac's 120 s DEFAULT\_TIMEOUT (verify\_ac.py:2888), so `verify_ac.py run --id BG1694 --dry-run` reports AC4 FAIL by timeout while pytest alone passes it. The census module is unchanged since the base ref (empty diff) and no open bug covers its runtime; RULINGS: The AC4 reopening is CLOSED: the census at e14e7052a named both cases (:155 and :253) and at 06cc6ca01 passes (4 passed, 32 subtests). The rest was judged by execution in detached worktrees at 06cc6ca01. The "ignores its bound" mutant is still killed without timing, on both modules (`_child` handed 30 and `_pid` deadline +30 fail on `clock.now` 30.0 not less than 1). An unbounded loop that keeps sleeping is ended by the clock's limit as a named failure, not hidden (the regex mismatch on "the wait ran past 60 s"). The two modules pass with the importer test\_lane\_land\_brief\_bound\_group.py in one session under `-n 4` (19 passed, 4 subtests) and serially, and the four new cases pass under the unittest fallback the commit hook uses, so `sys.modules[__name__]` patches the module the waits read in each mode. verify\_ac passes AC1 to AC3. Remark, not a finding: a wait that overshoots its 0.2 s bound by 0.5 s survives in both modules, inside the documented one-second ceiling, so a tighter ceiling such as one sleep step past the bound would pin it for free. Not run: the full suite on the gate host.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1694 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1694 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the stand-in clock moves only inside its `sleep`, so a wait that polls `monotonic()` without sleeping never reaches its bound or the clock's limit and hangs the case: with `time.sleep(0.01)` dropped from `_wait_for` (test\_kill\_grace\_interrupt.py:57) or from `_pid` (test\_lane\_land\_commit\_timeout\_group.py:121), a bounded busy wait the wall clock would end at 0.2 s, `test_child_gives_up_at_its_bound` and `test_pid_gives_up_at_its_bound` each hung until a 60 s wall bound killed them, and no pytest-timeout is installed to end such a hang in the gate. That falsifies the round's own claim that "a loop that never gives up ends the case instead of hanging it" in both `_Clock` docstrings (test\_kill\_grace\_interrupt.py:68-72, test\_lane\_land\_commit\_timeout\_group.py:86-90) and in both `test_the_clock_ends_a_wait_that_never_gives_up` cases, which pin only a loop that keeps sleeping. A `monotonic()` that also moves the clock on and enforces the limit, with a case pinning it, or a claim narrowed to a wait that keeps sleeping, closes it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] AC4's Verify, `tools/tests/test_test_census.py::WallClockCensusTests`, ran 198 s and 207 s here at load average 12, past verify\_ac's 120 s DEFAULT\_TIMEOUT (verify\_ac.py:2888), so `verify_ac.py run --id BG1694 --dry-run` reports AC4 FAIL by timeout while pytest alone passes it. The census module is unchanged since the base ref (empty diff) and no open bug covers its runtime
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1694 AC1 still passes: Given the machine under load, when `test_kill_grace_interrupt.py` runs, then `KillGraceInterruptTests._child` waits under a bound (`_wait_for`) until child.pid holds an integer before reading it. Fails on: `ValueError: invalid literal for int() with base 10: ''` at `_child`, which refused run twenty-three's push of e2a109be on the gate host.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py
  - **Verified:** yes (2026-11-23)
- [ ] **AC4** BG1694 AC2 still passes: Given the deaf child in `test_kill_grace_interrupt.py`, when it records its pid, then it writes a temporary name and moves it into place with `os.replace`, so a reader never sees an empty child.pid. Fails on: `open(path, 'w').write(pid)`, which creates the file empty before writing.
  - **Verify:** shell grep -q 'os.replace' .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py && python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py
  - **Verified:** yes (2026-11-23)
- [ ] **AC5** BG1694 AC3 still passes: Given the machine under load, when `test_lane_land_commit_timeout_group.py` runs, then `LandCommitTimeoutKillsHooksTests._pid` waits under a bound until the hook's pid file holds an integer before reading it, and the hook writes it atomically. Fails on: `ValueError: invalid literal for int() with base 10: ''` from `_pid`, as a run twenty-three commit hit at load 13.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_commit_timeout_group.py
  - **Verified:** yes (2026-11-23)
- [ ] **AC6** BG1694 AC4 still passes: Given the wall-clock census, when `tools/tests/test_test_census.py` runs, then neither new bound test (`test_child_gives_up_at_its_bound`, `test_pid_gives_up_at_its_bound`) is named as a commit-run test bounding a duration its own process measures: each is marked `serial_only` (or `boundary_only`) or bounds nothing by wall clock. Fails on: the two `assertLess(time.monotonic() - started, 10, ...)` lines landed in e14e7052, which refused REF2's commit.
  - **Verify:** pytest tools/tests/test_test_census.py::WallClockCensusTests
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
