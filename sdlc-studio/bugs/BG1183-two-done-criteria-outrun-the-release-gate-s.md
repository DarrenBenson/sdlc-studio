# BG1183: Two Done criteria outrun the release gate's verify ceilings: US0940's test takes up to 535 s and US0926's migrate dry run 180 s

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_release_verify.py, .claude/skills/sdlc-studio/scripts/migrate.py, changelog.d/BG1183.md, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:07:17Z

## Summary

Found at the 6.2.0 release (2026-11-02). `gate.py --release` gives each verifier 300 s (`SDLC_VERIFY_TIMEOUT).` US0940 AC1 (`test_lean_release_verify.py`, BG1100) passed alone in 534.65 s on a quiet machine and timed out under 450 s, so the gate had to run with 900 s (D0398). US0926 AC1's `migrate.py` dry run took 180 s, over `verify_ac`'s 120 s default. BG1100 records the first, and the second is new.

## Steps to Reproduce

1. `time python3 -m pytest -q tools/tests/test_lean_release_verify.py`.
2. `time python3 .claude/skills/sdlc-studio/scripts/migrate.py`.

## Proposed Fix

Make each criterion's verifier finish well under 300 s (scope US0940's test to the criteria still worth re-running, and find why migrate's dry run is slow), or give the criterion a declared timeout the gate reads.

## Acceptance Criteria

- [ ] **AC1** `gate.py --release` passes US0940 AC1 and US0926 AC1 under its default 300 s ceiling.
  - **Verify:** pytest tools/tests/test_lean_release_verify.py

## Impact

A release gate on an ordinary machine goes red on a passing test unless someone raises the ceiling by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
