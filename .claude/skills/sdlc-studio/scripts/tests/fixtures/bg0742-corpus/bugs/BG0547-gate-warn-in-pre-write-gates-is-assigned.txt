# BG0547: one advisory silently replaces another: the transition gate ladder assigns its warning variable where its own docstring says the warnings accumulate

> **Status:** Won't Fix
> **Closed with findings in:** Already repaired, measured 2026-08-13. The fix landed in the interim and the bug was never closed - see the BG0577 finding, which is that nothing detects this state. Verified by reading the code this bug describes.
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01KZEF9M plan review of BG0541, 2026-08-07, qa seat. Pre-existing at the base ref.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_pre_write_gates` documents at transition.py:854 that its advisory warnings accumulate. At transition.py:975 the depth-parity advisory ASSIGNS `gate_warn` outright. The AC-verify advisory further down does concatenate onto it, so the two paths disagree about what the variable means: whichever fires first can be discarded, and which survives depends on statement order rather than on anything a reader would predict. A project running with `quality.depth_parity_gate` off and `quality.done_requires_verified` off gets one of its two advisories and no indication the other fired.

## Steps to Reproduce

1. Read transition.py:854 - the docstring states the warnings accumulate. 2. Read transition.py:975 - `gate_warn = f"depth-parity advisory: {parity}"`, a plain assignment. 3. Compare with the AC-verify arm below it, which does `gate_warn = f"{gate_warn}; {verify_warn}" if gate_warn else verify_warn`. 4. Arrange a fixture where both advisories are live and read the output.

## Proposed Fix

Accumulate in both arms through one helper, so the two cannot disagree, and add a test whose fixture fires both advisories at once and asserts each appears. Found by the qa seat reviewing BG0541's test plan; reported as pre-existing at the run's base ref, not introduced by it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_pre_write_gates` documents at transition.py:854 that its advisory warnings accumulate.
- [ ] **AC2** The proposed fix lands, pinned by a test: Accumulate in both arms through one helper, so the two cannot disagree, and add a test whose fixture fires both advisories at once and asserts each appears.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
| 2026-08-07 | sdlc-studio | The CODE fix shipped with BG0541: the depth-parity arm now accumulates onto `gate_warn` through the same shape the AC-verify arm uses, because the mutation lane's only reporting path would otherwise have been thrown away by it. The bug stays OPEN because its own criterion and the test that pins it are still owed - a fixture firing both advisories at once and asserting each appears - and closing it on somebody else's diff would be a status its body cannot support. Groom it into a batch |
