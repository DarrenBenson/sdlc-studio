# BG1160: gate.py --run-tests prints 'no tests ran' and exits 0 when one of its modules is missing, even if a real module beside it fails

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, changelog.d/BG1160.md
> **Evidence:** BG1065 builder report, 2026-11-01, outside-the-unit item 2 (reproduced).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T06:33:50Z

## Summary

Found and reproduced by BG1065's builder (2026-11-01): `gate.py --run-tests <real module> <nonexistent path>` prints 'no tests ran' and exits 0, even when the real module has a failing test. A missing path turns the whole run into a vacuous green, and the failure in the real module is lost. A false green is the defect class this repository guards hardest against (LL0008).

## Steps to Reproduce

1. In a throwaway worktree, make one test in a real module fail.
2. `python3 .claude/skills/sdlc-studio/scripts/gate.py --run-tests <that module> tests/does_not_exist.py`.
3. Expected: a non-zero exit naming the failure and the missing path. Actual: 'no tests ran', exit 0.

## Proposed Fix

Refuse a --run-tests path that does not exist by name before running anything, and never report 'no tests ran' when any named module was collected.

## Acceptance Criteria

- [ ] **AC1** A --run-tests path that does not exist is refused by name, non-zero, before any test runs.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py
- [ ] **AC2** With every path real, a failing test fails the run (the positive control).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py

## Impact

A caller that passes one stale path gets a green gate over a red module.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
