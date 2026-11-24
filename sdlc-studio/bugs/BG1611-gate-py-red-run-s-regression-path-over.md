# BG1611: gate.py --red-run's regression path over-claims: a failing id that names no file files no bug, and a second red on a different test reuses the first bug without naming that test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/test_ci_red_run_policy.py, changelog.d/BG1611.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** run eighteen, 2026-11-19: US1238 verdict files sdlc-studio/reviews/verdicts/US1238/c5fd391ac1ed-0cec25b0.txt and abc29ff3d2a5-cead0cd7.txt, non-blocking findings
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T13:23:27Z

## Summary

Two non-blocking findings from US1238's review (run eighteen, both seats). A regression whose failing ids name no file in the tree (a Go `TestFoo`, a jest test title) exits 2 asking the operator to file it, while help/gate.md and the changelog say a bug is always filed naming the run and the test. And a second red of a regression run on a different failing test answers with the first run's bug (gate.py around line 3231) but never records the new test on it.

## Steps to Reproduce

`gate.py --red-run 9 --failed TestFoo` exits 2 with 'file it with `file_finding.py`'. Then `--red-run 12 --failed tests/test_c.py::T::t` files a bug, and `--red-run 12 --failed tests/test_b.py::T::t` answers 'filed as' that bug, which never names `test_b.`

## Proposed Fix

File the regression bug for any failing id, naming the id verbatim when it is not a path, and record each further failing test of the same run on its bug; or narrow help and the changelog to what the code does.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Two non-blocking findings from US1238's review (run eighteen, both seats).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: `gate.py --red-run 9 --failed TestFoo` exits 2 with 'file it with `file_finding.py`'.
- [ ] **AC3** The proposed fix lands, pinned by a test: File the regression bug for any failing id, naming the id verbatim when it is not a path, and record each further failing test of the same run on its bug; or...

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. Red-run over-claims in help.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
