# BG1195: Four test modules of tools/remote-gate.sh name no test-census-subject, so a commit to the script runs only one of the five

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_remote_gate_push.py, tools/tests/test_remote_gate_runs.py, tools/tests/test_remote_gate_doctor.py, tools/tests/test_run_suite_remote.py, changelog.d/BG1195.md
> **Evidence:** US1114 builder report, 2026-11-04, outside-the-unit item 2.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T08:56:15Z

## Summary

2026-11-04, US1114's build (run five). Before US1114, a commit to `tools/remote-gate.sh` selected no test module (the BG1115 family). US1114's new `test_remote_gate_release.py` names the script as its `test-census-subject`, but `test_remote_gate_push.py`, `test_remote_gate_runs.py`, `test_remote_gate_doctor.py` and `test_run_suite_remote.py` still do not. A commit to the script therefore runs one of its five modules, and the other four wait for the push gate.

## Steps to Reproduce

1. `grep -L test-census-subject tools/tests/test_remote_gate_*.py tools/tests/test_run_suite_remote.py`.
2. Stage an edit to tools/remote-gate.sh and read the modules the pre-commit selection names.

## Proposed Fix

Add the script as a `test-census-subject` in each of the four modules.

## Acceptance Criteria

- [ ] **AC1** Every test module that exercises tools/remote-gate.sh names it as a test-census-subject.
  - **Verify:** shell test -z "$(grep -L 'test-census-subject.*remote-gate.sh' tools/tests/test_remote_gate_push.py tools/tests/test_remote_gate_runs.py tools/tests/test_remote_gate_doctor.py tools/tests/test_run_suite_remote.py)"

## Impact

A defect in remote-gate.sh that only those four modules catch passes the commit and is first seen at the push gate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
