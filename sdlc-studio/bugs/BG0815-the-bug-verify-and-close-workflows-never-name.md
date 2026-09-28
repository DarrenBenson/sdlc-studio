# BG0815: The bug verify and close workflows never name verify_ac.py, so an agent runs the tests by hand and the criterion is never recorded green

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_bug_verify_step.py, changelog.d/BG0815.md
> **Evidence:** US0963 eval run v6-main, scenario 06-independence-gate EB2 (blocking) fail; transcript /tmp/evals-v6-main/06-independence-gate.transcript.txt; grader report 2026-09-28; operator ruling D0279
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T10:42:41Z

## Summary

Eval 06-independence-gate, clean run against main ff9d9b9f (2026-09-28, run v6-main), failed blocking EB2: the worker ran python3 -m unittest by hand; no verify-report.json, no Verified stamp, AC1 unticked. The grader traced it to the guidance: reference-bug.md's verify workflow step 3 says 'Execute tests listed in Tests Added' and the close workflow says transition.py reads the bug's criteria, and neither names `verify_ac.py` run, the one command that records a criterion green (grep -n `verify_ac` reference-bug.md help/bug.md finds nothing). A worker following the docs verifies by hand, so Fixed either stands on an unrecorded run or is refused later for a reason the docs never gave.

## Steps to Reproduce

Set up evals/scenarios/06-independence-gate.json; run a fresh session against main's skill; the worker runs the unit tests directly and never runs `verify_ac.py.`

## Proposed Fix

Name `verify_ac.py` run --id BG{NNNN} in the bug verify workflow's run-tests step and in the close workflow's evidence step (and help/bug.md's verify and close entries), saying it records each criterion's result that transition.py then reads; running the tests by hand records nothing.

## Acceptance Criteria

- [ ] **AC1** Given reference-bug.md's verify and close workflows and help/bug.md's verify and close entries, then each names `verify_ac.py` run --id as the way a bug's criteria are recorded green before Fixed, and none tells the agent only to execute the tests. Fails on: the rc.1 wording, which says 'Execute tests listed in Tests Added' and never names the verifier
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_bug_verify_step.py::BugVerifyStepTests::test_the_verify_and_close_steps_name_the_verifier
  - **Verified:** yes (2026-09-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
