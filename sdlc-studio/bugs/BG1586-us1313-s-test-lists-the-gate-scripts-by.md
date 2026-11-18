# BG1586: US1313's test lists the gate scripts by name without declaring the list HAND-MAINTAINED ON PURPOSE, so the hand-copied-list guard reddened the push

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_repo_risk_map.py, tools/tests/test_test_census.py
> **Evidence:** Run sixteen push, 2026-11-18, .local/run16/push3.log line 17.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T08:57:17Z

## Summary

tools/tests/`test_repo_risk_map.py` (US1313) names gate.py, critic.py, transition.py, sprint.py and `verify_ac.py` in one literal. `test_test_census.py`'s HandCopiedMirrorTests reads any three shipped script names in a row as a copy of a production-owned set and refuses it, unless the file carries the HAND-MAINTAINED ON PURPOSE marker. Here the list is the assertion itself (D0520 names which scripts are high), not a mirror of one, so it should be declared. The push gate's full suite failed on it at commit 4ed7d225: 1 failed, 9218 passed.

## Steps to Reproduce

At 4ed7d225 run pytest tools/tests/`test_test_census.py` -k `test_no_new_hand_copied_script_list`; it fails naming `test_repo_risk_map.py.`

## Proposed Fix

Declare the list in `test_repo_risk_map.py` with the HAND-MAINTAINED ON PURPOSE marker and a one-line reason naming D0520; do not add the file to the shrink-only `_KNOWN_MIRRORS` set.

## Acceptance Criteria

- [ ] **AC1** Given `tools/tests/test_repo_risk_map.py` naming the gate scripts, when the hand-copied-list guard scans both suite directories, then it reports no offender and its shrink-only `_KNOWN_MIRRORS` set is unchanged. Fails on: `test_repo_risk_map.py` still listed, or the file added to `_KNOWN_MIRRORS` to pass.
  - **Verify:** pytest tools/tests/test_test_census.py::HandCopiedMirrorTests
  - **Verified:** yes (2026-11-18)
- [ ] **AC2** Given the fixed test module, when it is read and run, then it carries the `HAND-MAINTAINED ON PURPOSE` marker beside a reason naming D0520 and its own tests still pass. Fails on: a marker with no reason, or the module's tests red.
  - **Verify:** shell grep -q 'HAND-MAINTAINED ON PURPOSE' tools/tests/test_repo_risk_map.py && grep -q D0520 tools/tests/test_repo_risk_map.py && python3 -m pytest -q tools/tests/test_repo_risk_map.py
  - **Verified:** yes (2026-11-18)

## Impact

The push is refused, so none of run sixteen reaches origin.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
