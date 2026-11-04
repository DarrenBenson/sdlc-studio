# BG1183: Two Done criteria outrun the release gate's verify ceilings: US0940's test takes up to 535 s and US0926's migrate dry run 180 s

> **Status:** Fixed
> **Severity:** Low
> **Points:** 5
> **Affects:** tools/tests/test_lean_release_verify.py, .claude/skills/sdlc-studio/scripts/migrate.py, changelog.d/BG1183.md, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, sdlc-studio/stories/US0940-every-criterion-on-a-done-story-passes-when.md
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

Widened under D0403 (2026-11-04) after the first build, 791c5107, took the dry run from 415 s to about 150 s and AC2 still timed out at 120 s. That build measured the remaining cost outside the first Affects: the conformance step's 266 pytest collections (`conformance.py` and `verify_ac.py`; skipping units the adoption cutoff exempts is one lever), `project_upgrade.audit` running `validate_file` over 3,333 files (10 to 17 s), and the conformance lane re-reading the critic ledgers for every unit (20 to 37 s). US0940 AC1's text says each measured criterion is executed, and the first build now resolves five bare-node criteria instead of running them, so the criterion is re-pointed in this unit, never retired (LC-015).

## Acceptance Criteria

- [ ] **AC1** US0940 AC1's verifier, `tools/tests/test_lean_release_verify.py`, finishes inside the release gate's default 300 s ceiling, and still fails on each measured criterion it re-runs when that criterion is red.
  - **Verify:** shell timeout 300 python3 -m pytest -q tools/tests/test_lean_release_verify.py
  - **Verified:** yes (2026-11-04)
- [ ] **AC2** US0926 AC1's `migrate.py` dry run on this repository finishes inside verify_ac's default 120 s ceiling.
  - **Verify:** shell timeout 120 python3 .claude/skills/sdlc-studio/scripts/migrate.py
  - **Verified:** yes (2026-11-04)

## Impact

A release gate on an ordinary machine goes red on a passing test unless someone raises the ceiling by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Re-groomed for run five (goal review, all three seats): the Verify ran the whole module, which passes today, just slowly; each criterion is now a timing-bound check that is red today (534.65 s and 180 s measured 2026-11-02). Points 1 to 2 |
| 2026-11-04 | Claude Opus 5.5 (orchestrator) | Widened under D0403: 5 points, Affects add conformance.py, `verify_ac.py`, `project_upgrade.py`, their tests and US0940's story file, so AC2's 120 s can be met |
