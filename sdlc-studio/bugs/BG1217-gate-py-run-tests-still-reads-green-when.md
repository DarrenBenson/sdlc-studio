# BG1217: gate.py --run-tests still reads green when a selector names a test that does not exist in a file that does, beside a failing module, under xdist

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_run_tests_paths.py, changelog.d/BG1217.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** BG1160 round-1 verdict, scratchpad run5/BG1160-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T19:15:31Z

## Summary

2026-11-04, BG1160's review (pre-existing). BG1160 refuses a selector whose path is missing. A node id whose file exists but whose test does not, `test_red.py sub/test_ok.py::nope`, still exits 0 under xdist with the red test never run, as it did before BG1160. BG1160's Proposed Fix (never report 'no tests ran' when any named module was collected) is half delivered. The commit hook never hits it, since its selection names whole modules on disk.

## Steps to Reproduce

1. A fixture with a failing tests/`test_red.py` and a passing sub/`test_ok.py.`
2. `gate.py --run-tests test_red.py sub/test_ok.py::nope` with pytest-xdist installed: exit 0.

## Proposed Fix

Treat pytest's exit 4 or 5 with any named module collected as a refusal naming the unresolved node, or resolve node ids before the run.

## Acceptance Criteria

- [ ] **AC1** `--run-tests` beside a failing module with a node id naming no test exits non-zero and names the node.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_run_tests_paths.py
  - **Verified:** yes (2026-11-05)

## Impact

A hand-run gate over a mistyped node id passes beside a real failure.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
