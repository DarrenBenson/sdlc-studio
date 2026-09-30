# BG0843: migrate names no engagement-floor cutoff, so a v4.1 project's gate fails the engagement floor on 349 shipped units before and after the upgrade and the report says nothing

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, changelog.d/BG0843.md
> **Evidence:** docs/upgrade-rehearsal-v6.md (US0962), v4.1 row, gate before and after; `migrate.py` `_conformance_cutoff` covers only the conformance lane; BG0785 AC notes
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T19:42:39Z

## Summary

US0962 rehearsal (a v4.1 project of 687 stories, skill 6.0.0-rc.1 at 5e45cbf9): `gate.py` fails its engagement-floor lane on '349 shipped unit(s) below the engagement floor (no plan and not shown small): BG0001, BG0002, ...' before and after `migrate --apply`, and neither the dry run nor the apply mentions the engagement floor. BG0785 made migrate name the `conformance.adopt_after` cutoff for the conformance lane and explicitly left the engagement floor out ('has its own cutoff and is not part of this bug'). The project sets no `engagement_floor.adopt_after`; the v2.4 project in the same rehearsal sets 541 and its lane passes. An upgrader learns of the 349 units only from the gate.

## Steps to Reproduce

On a fixture with shipped bugs that carry no criterion, no Verify line, no plan and no Affects, and no `engagement_floor.adopt_after`, run `migrate.py --root <fixture>`: no item names the engagement floor, while `gate.py --root <fixture>` fails the engagement-floor lane.

## Proposed Fix

Mirror `_conformance_cutoff` for the engagement floor: ask the engagement-floor lane which shipped units it would fail and report them as one needs-a-human item carrying the exact `engagement_floor.adopt_after: <id>` line (the highest failing id), never written. Report only; no new check (LC-008).

## Acceptance Criteria

- [ ] **AC1** Given a fixture whose engagement-floor lane fails N shipped units and which sets no `engagement_floor.adopt_after`, when `migrate.py --format json` runs (dry or --apply), then one needs-a-human item names the N units and the `engagement_floor.adopt_after: <highest failing id>` line, and `.config.yaml` is unchanged. Fails on: today's migrate, which names nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::EngagementFloorCutoffTests::test_migrate_names_the_engagement_floor_cutoff
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given the same fixture with an `engagement_floor.adopt_after` at or above every failing id, then migrate names no engagement-floor item. Fails on: a cutoff proposed below one already set
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::EngagementFloorCutoffTests::test_a_cutoff_already_covering_every_unit_names_nothing
  - **Verified:** yes (2026-09-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
