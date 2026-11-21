# BG1677: lane land's sibling-script timeout stops only the script, leaving its child processes running

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_script_timeout_group.py, changelog.d/BG1677.md
> **Evidence:** Run twenty-one lane L builder noted it while building BG1610 and BG1627; confirmed by reading lib/lanes.py:817-827 at b771e799.
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T10:37:59Z

## Summary

lib/lanes.py `_script` runs a sibling script (`verify_ac.py` among them) through subprocess.run with a timeout. On TimeoutExpired, subprocess.run kills only the direct child, so the processes that script started (`verify_ac`'s pytest runs) keep running after lane land has reported the script stopped. This is the same fault BG1610 fixes for the commit and BG1627 for the qa brief.

## Steps to Reproduce

Read lib/lanes.py `_script` (subprocess.run([...], timeout=timeout) with no new session and no process-group kill). Run lane land on a unit whose `verify_ac` run outlasts the timeout: lane land reports the script stopped, while its pytest children keep running.

## Proposed Fix

Run `_script` through the bounded runner lane L's units introduce (`lanes._bounded`: its own session, the whole process group killed on timeout), and pin it with a test whose script starts a child that outlives the bound.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: lib/lanes.py `_script` runs a sibling script (`verify_ac.py` among them) through subprocess.run with a timeout.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read lib/lanes.py `_script` (subprocess.run([...], timeout=timeout) with no new session and no process-group kill).
- [ ] **AC3** The proposed fix lands, pinned by a test: Run `_script` through the bounded runner lane L's units introduce (`lanes._bounded`: its own session, the whole process group killed on timeout), and pin it...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
