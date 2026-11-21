# BG1575: BG0660's unscoped-boundary guard flags a --run-tests call that runs no other lane, and is satisfied by an --only that call ignores

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/gate.py, changelog.d/BG1575.md
> **Evidence:** BG1519 QA verdict, sdlc-studio/reviews/verdicts/BG1519/b4860a569b60-148ea286.txt; test_gate.py near line 5486 at 85b79786.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T01:40:41Z

## Summary

BoundaryGateIsNeverDrivenUnscopedTests (`test_gate.py)` refuses any test that passes `--boundary push` to gate.py without a scoping flag. A `gate.py --run-tests <module> --boundary push` call runs only the named modules, so it pays no other lane, yet the guard refused BG1519's new test for it. Run sixteen satisfied the guard by adding `--only unit-tests`, which the QA review of BG1519 showed `--run-tests` never reads: the guard is read as text, so a flag with no effect passes it.

## Steps to Reproduce

Write a test calling gate.py with --run-tests tools/tests/x.py --boundary push; the guard refuses it. Add --only unit-tests; the guard passes, and the gate's behaviour is unchanged.

## Proposed Fix

Treat --run-tests as scoping in the guard, and either make gate.py refuse --only beside --run-tests or honour it; then drop the --only from BG1519's test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BoundaryGateIsNeverDrivenUnscopedTests (`test_gate.py)` refuses any test that passes `--boundary push` to gate.py without a scoping flag.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Write a test calling gate.py with --run-tests tools/tests/x.py --boundary push; the guard refuses it.
- [ ] **AC3** The proposed fix lands, pinned by a test: Treat --run-tests as scoping in the guard, and either make gate.py refuse --only beside --run-tests or honour it; then drop the --only from BG1519's test.

## Impact

Tests carry flags that do nothing to satisfy a guard, and a reader takes them as meaningful.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. A test guard in this repository refuses a --run-tests call that pays no other lane; the author scopes the call, so the cost is one rewording. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
