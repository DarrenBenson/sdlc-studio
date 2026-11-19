# BG1612: Two of gate.py --red-run's behaviours hold by probe but no test pins them: the sections after a bug's CI Red Runs section, and the refusal of a negative, boolean or fractional rerun limit

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_ci_red_run_policy.py, changelog.d/BG1612.md
> **Evidence:** run eighteen, 2026-11-19: US1238 engineering verdict sdlc-studio/reviews/verdicts/US1238/abc29ff3d2a5-cead0cd7.txt, findings 5 and 6
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T13:23:36Z

## Summary

From US1238's engineering review (run eighteen). The branch that keeps the sections after `## CI Red Runs` (gate.py around lines 3209-3210) is reached by no test, because every fixture's section is the last in the file, so a mutant dropping `if sep:` survives and would drop a `## Notes` section on the next red. `_rerun_limit`'s refusal of -1, true, 'two' and 1.5 (gate.py around line 3220) holds by probe, but mutants dropping `limit < 0` or the bool guard survive the suite.

## Steps to Reproduce

Delete `if sep:` and its line in gate.py's red-run recorder, or drop the `limit < 0` guard in `_rerun_limit`, then run `test_ci_red_run_policy.py`: every test still passes.

## Proposed Fix

Add a fixture whose CI Red Runs section is followed by another section, and a test per refused limit value, each asserting nothing is recorded.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From US1238's engineering review (run eighteen).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Delete `if sep:` and its line in gate.py's red-run recorder, or drop the `limit < 0` guard in `_rerun_limit`, then run `test_ci_red_run_policy.py`: every test...
- [ ] **AC3** The proposed fix lands, pinned by a test: Add a fixture whose CI Red Runs section is followed by another section, and a test per refused limit value, each asserting nothing is recorded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
