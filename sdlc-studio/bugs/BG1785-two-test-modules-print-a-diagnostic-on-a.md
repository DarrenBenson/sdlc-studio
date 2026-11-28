# BG1785: Two test modules print a diagnostic on a green run, so main's full suite is over its noise budget and the push gate refuses it

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, tools/test-noise-baseline.json, changelog.d/BG1785.md
> **Evidence:** Run twenty-eight's third push of main (2026-11-28, about 02:25Z): devserver1 refused 3eec27935 at the green-run noise gate after the full suite passed (1306 s); .local/run28/push-3.log lines 20-29.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T02:26:43Z

## Summary

The push boundary's green-run noise gate refused 3eec27935: a passing full run printed 106 diagnostic lines against the recorded total of 104 (tools/test-noise-baseline.json). Measured alone, `test_solution_review_record.py` prints 2 ("warning: could not load .config.yaml (while parsing a flow sequence" and "review: [unclosed", from its malformed-config case at line 266), and `test_cost_anatomy.py` prints 1 ("WARNING: author 'agent-zz' lacks the `<holder> (<role>)` form ...", from `record_verdict` calls with author="agent-zz"). Neither module has an entry in the baseline, so each counts against zero. The tests pass; the leak is that the tool's warning reaches the console instead of being captured and asserted on.

## Steps to Reproduce

1. cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_solution_review_record 2>&1 | python3 ../../../../tools/test_noise.py --budget ../../../../tools/test-noise-baseline.json --select test_solution_review_record
2. It reports 2 diagnostic lines above a budget of 0. The same for tests.test_cost_anatomy reports 1.

## Proposed Fix

Capture each warning in the test that provokes it (`contextlib.redirect_stderr`) and assert on the captured text, so the run says nothing. Record `test_solution_review_record` and `test_cost_anatomy` in tools/test-noise-baseline.json at 0. Lower, never raise, an entry.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The push boundary's green-run noise gate refused 3eec27935: a passing full run printed 106 diagnostic lines against the recorded total of 104...
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_a_malformed_setting_is_refused_by_name
  - **Verified:** yes (2026-11-28)
- [ ] **AC2** The proposed fix lands, pinned by a test: Capture each warning in the test that provokes it (`contextlib.redirect_stderr`) and assert on the captured text, so the run says nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_a_project_declared_seat_is_read_as_a_seat
  - **Verified:** yes (2026-11-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
