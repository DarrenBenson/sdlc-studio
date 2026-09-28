# BG0829: A unit carried at the review cap is filed as an ungroomed bug that sprint plan cannot take, and every carry prints that the operator was notified

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_groomed.py, changelog.d/BG0829.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** soak F40 (website project, round-2 REJECT); HEAD 7e53a438 critic.py carry_at_cap (~1535-1560) and panel_escalation (~1425-1440); sdlc-studio/bugs/BG0775 header
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:31Z

## Summary

`critic.carry_at_cap` files the carried bug with the unit's Affects and Points but no criteria and no Verify lines (placeholder criteria restate the summary), its Proposed Fix is `deliver <unit> again in a later run`, its title and slug spell the unit hyphenless, and it is stamped `Raised-in-batch: none open - raised outside a delivery batch` although it is raised inside the open run (BG0775, carried in Sprint 4, reads the same). It cannot be planned without hand grooming. `panel_escalation` prints `ESCALATED to the operator ... The operator is NOTIFIED` on every carry, and nothing notifies anyone.

## Steps to Reproduce

Record a round-2 REJECT at the cap for a unit in an open run: read the filed bug's criteria, Verify lines, Raised-in-batch and title; read the record output.

## Proposed Fix

Carry the unit's own criteria and Verify lines onto the bug (they are what the redelivery must pass), spell the unit in its file form, stamp the open run as the raising batch, and say `the operator reads this on the report` instead of NOTIFIED.

## Acceptance Criteria

- [ ] **AC1** Given a unit with two criteria carried at the cap in an open run, then the filed bug carries both criteria with their Verify lines, names the run in Raised-in-batch, and `sprint plan` accepts it. Fails on: HEAD's placeholder criteria and `none open`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_groomed.py::CarryBugGroomedTests::test_the_carried_bug_can_be_planned
- [ ] **AC2** Given a carry, then the record output does not claim the operator was notified. Fails on: HEAD's NOTIFIED line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_groomed.py::CarryBugGroomedTests::test_no_notification_is_claimed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
