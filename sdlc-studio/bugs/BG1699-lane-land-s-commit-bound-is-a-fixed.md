# BG1699: lane land's commit bound is a fixed 1800 seconds that no setting or flag changes, so a lane whose commit selects most of the suite is stopped whenever the host is loaded

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run twenty-two, 2026-11-22: lane D's land stopped at the bound three times (land-D.log, land-D4.log, land-D5.log), once with the host at load 1.7 when it started; lib/lanes.py:121 COMMIT_TIMEOUT = 1800
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T09:51:47Z

## Summary

sprint lane land commits through the repository's hooks under `COMMIT_TIMEOUT`, a constant 1800 s in lib/lanes.py that no config key or flag overrides. A commit whose hooks select most of the suite takes about 26 minutes on this repository's workstation unloaded, so any other work on the host (a second lane's tests, another project's build) pushes it past the bound and the land stops with nothing committed. A project with slower hooks cannot land at all. The only way through is to commit in the worktree by hand and re-run the land.

## Steps to Reproduce

1. Stage a lane whose change touches sprint.py, so the pre-commit hook selects about 5,000 tests (about 1,600 s here). 2. Run any other CPU-bound work on the host. 3. Run sprint.py lane land --worktree <wt> --units <ids>. 4. It prints 'the commit's hooks ran past 1800s and were stopped, so nothing was committed'; there is no option to give it longer.

## Proposed Fix

Read the bound from a setting (for example `lanes.commit_timeout` in config-defaults.yaml, default 1800) and a --commit-timeout flag on lane land, and name both in the stop message.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: sprint lane land commits through the repository's hooks under `COMMIT_TIMEOUT`, a constant 1800 s in lib/lanes.py that no config key or flag overrides.
- [ ] **AC2** The proposed fix lands, pinned by a test: Read the bound from a setting (for example `lanes.commit_timeout` in config-defaults.yaml, default 1800) and a --commit-timeout flag on lane land, and name...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
