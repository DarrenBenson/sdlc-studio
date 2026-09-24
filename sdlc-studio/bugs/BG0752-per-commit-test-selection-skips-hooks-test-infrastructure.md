# BG0752: Per-commit test selection skips hooks, test infrastructure and code reached through another script

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** US0880 review findings 1-2, RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0880's selection follows direct edges only. A change to `.githooks/*`, `tools/tests/conftest.py`, `pytest.ini`, `tools/skill-tests.sh` or a test helper selects zero modules (before: 68-80), and a `lib/` helper reached only through another script selects none of the tests that exercise it (e.g. `lib/tiers.py` -> `test_planning_tier`). The full suite at push catches them; the commit does not.

## Steps to Reproduce

1. Mutate `lib/tiers.py` `promotion_deficit` to `return None`. 2. `gate.py --suite-decision --changed .claude/skills/sdlc-studio/scripts/lib/tiers.py` answers mode none. 3. `test_planning_tier.py` has 3 failures.

## Proposed Fix

Route hook, test-infrastructure and test-helper paths to the modules that name them by path, and follow one level of script-to-script import for `lib/`.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0880's selection follows direct edges only.
- [ ] **AC2** The proposed fix lands, pinned by a test: Route hook, test-infrastructure and test-helper paths to the modules that name them by path, and follow one level of script-to-script import for `lib/`.

## Impact

US0880's selection follows direct edges only.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
