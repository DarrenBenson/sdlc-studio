# BG1647: TrdCoverageSoftDependencyTests' Done-gate half misses its patch in the gate's parallel run, so the push gate goes red

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** tools/tests/test_trd_coverage_soft_dependency.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T01:52:25Z

## Summary

BG1096 (6aee7a42, RUN-01M7TTK3) added tools/tests/`test_trd_coverage_soft_dependency.py.` Its `_gate` helper hides the coverage module by patching `verify_ac.coverage_report` on the module object the test imported, but `transition.line_coverage_lane` runs 'import `verify_ac` as `_va`' at call time (transition.py:807). In the gate's parallel suite on devserver1 a module object other than the patched one answers that import, so the real `coverage_report` runs, finds the plain temporary directory has no HEAD, and the block-mode lane reports 'base ref HEAD does not resolve here' instead of the absent-module refusal: `test_the_run_exits_2_and_the_done_gate_splits_block_from_report` fails at line 96. It passes when the module runs alone. The push boundary gate refused 682c3469 on it.

## Steps to Reproduce

Run the push boundary gate (or the full suite in parallel) on a tree holding tools/tests/`test_trd_coverage_soft_dependency.py`: `test_the_run_exits_2_and_the_done_gate_splits_block_from_report` fails with 'base ref `HEAD` does not resolve here'. Run the module alone: it passes.

## Proposed Fix

Make the patch reach the module transition imports (patch sys.modules['`verify_ac`'] for the call, or patch the attribute on whatever module that import resolves to), and build the `_gate` fixture as a committed git repository as `_run_exit` does, so the lane would fail on the absent module even if the patch missed; prove it by running the module after a test that replaces sys.modules['`verify_ac`'].

## Acceptance Criteria

- [ ] **AC1** Given the gate's own suite runner (`tools/run-suite.sh`) or any test order, when `TrdCoverageSoftDependencyTests` runs, then its Done-gate half reports the absent-coverage refusal under `block` and the report-mode note under `report`, because the hidden module reaches the module object `transition.line_coverage_lane` imports and the fixture root resolves `HEAD`.
  - **Verify:** pytest tools/tests/test_trd_coverage_soft_dependency.py::TrdCoverageSoftDependencyTests::test_the_run_exits_2_and_the_done_gate_splits_block_from_report
  - **Verified:** yes (2026-11-20)
- [ ] **AC2** Fails on: the patch applied to a module object other than the one transition imports, or the fixture root left without a commit; a test in the module replaces `sys.modules['verify_ac']` before the gate half runs and still sees the absent-module refusal.
  - **Verify:** pytest tools/tests/test_trd_coverage_soft_dependency.py::TrdCoverageSoftDependencyTests::test_the_gate_half_holds_when_verify_ac_is_reimported
  - **Verified:** yes (2026-11-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
