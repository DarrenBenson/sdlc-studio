# BG1525: PRD section 9 says every gate-bearing key defaults on with one exception, but several shipped gate keys default off

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/prd.md, .claude/skills/sdlc-studio/reference-config.md, tools/tests/test_lean_prd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Section 9 Feature Flags, lines 657-662 (intro) against the table rows at 672 and 674, the Line coverage gate row (line 322) and the Project constitution row (line 268)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:29Z

## Summary

The introduction to the Feature Flags section of the PRD states a universal rule: for gate-bearing keys the default is ON, the opt-out is a recorded value, an absent config blocks, and `two_backlog.enforce` is the one deliberate exception. The shipped defaults and the PRD's own rows contradict it. In `templates/config-defaults.yaml`, `review.line_coverage` is off, `review.author_self_check` is report, `require_ac_verification` is false and `constitution.enforce` is false, and the PRD's table also lists `quality.require_full_sections` as off. For each of these an absent config leaves the gate disarmed. A reader rebuilding the product from the PRD would turn those gates on by default, or assume they are on, and an earlier correction to this section has gone stale again as shipped in 6.4.0.

## Steps to Reproduce

1. Read sdlc-studio/prd.md lines 657 to 662: the one-exception rule is stated.
2. Read .claude/skills/sdlc-studio/templates/config-defaults.yaml lines 64, 87, 117, 128 and 135: `line_coverage: off`, `author_self_check: report`, `require_ac_verification: false`, and `enforce: false` for both `two_backlog` and constitution.
3. Read the PRD rows at about lines 268, 322, 672 and 674: the PRD itself describes the constitution gate as opt-in, line coverage as off by default, and two further flags as false or off.
4. Read reference-config.md at about lines 296 to 298: the same universal sentence is repeated there.

## Proposed Fix

Reword the section 9 introduction to say which gate-bearing keys default on and to list every key that ships off or advisory, with the incremental-adoption reason each one carries, in place of the single-exception sentence. Make the same correction where reference-config.md repeats it. Add a check to the PRD refresh test that reads the defaults file and fails when the PRD names fewer default-off gate keys than the defaults file holds.

## Acceptance Criteria

- [ ] **AC1** Given the Feature Flags introduction in section 9 of `sdlc-studio/prd.md` and `templates/config-defaults.yaml`, when the two are compared, then the introduction names every gate-bearing key the defaults file ships off or advisory (`review.line_coverage`, `review.author_self_check`, `require_ac_verification`, `constitution.enforce`, `two_backlog.enforce` and `quality.require_full_sections` today), each with its incremental-adoption reason, and no longer calls `two_backlog.enforce` the one exception. Fails on: a PRD that names fewer default-off gate keys than the defaults file holds.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdFlagDefaultsTests::test_section_9_names_every_gate_key_that_ships_off
- [ ] **AC2** Given `reference-config.md`, when its statement of the gate-key default rule is read, then it carries the same correction and no single-exception sentence. Fails on: the reference still saying every gate-bearing key defaults on with one exception.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdFlagDefaultsTests::test_reference_config_does_not_claim_a_single_exception

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
