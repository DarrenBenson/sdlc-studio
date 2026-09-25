# US0952: An upgrader reads every v6 breaking change first

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** changelog.d/US0952.md, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_upgrade_breaking.py, tools/tests/test_lean_breaking_inventory.py
> **Epic:** EP0266
> **Points:** 2
> **Persona:** Jonah Reyes

## User Story

**As a** team lead upgrading a project from v5.1 to v6
**I want** the changelog and `project upgrade` to show the breaking changes first, each with what I must do
**So that** I act on the removed verbs, flags and keys before they refuse my scripts or CI

## Acceptance Criteria

- **AC1:** Given the 6.0.0 Breaking text (a `<!-- section: Breaking -->` fragment in `changelog.d/` before the cut, the `### Breaking` block under 6.0.0 in `CHANGELOG.md` after it), then it names every verb in `reference-scripts-surface.md` at tag v5.1.0 that is absent from it at the 6.0.0 tag (HEAD until that tag exists), every key present in `templates/config-defaults.yaml` at v5.1.0 and absent now, every id in `sdlc_md.RETIRED_CHECK_IDS` and the frozen ledgers, each with what to do, in at most 6 grouped bullets. Fails on: a hand list missing `autosprint.py preflight` or `validate.py warning-ratchet`; a test comparing against HEAD after the tag, which would demand 6.1's removals
  - **Verify:** pytest tools/tests/test_lean_breaking_inventory.py::BreakingInventoryTests::test_every_removed_surface_is_named
- **AC2:** Given a fixture CHANGELOG with 7 Added, 7 Changed, 7 Fixed and 2 Breaking entries for a version in range, when `project_upgrade.py` renders its capability digest, then the Breaking group prints first and uncapped. Fails on: HEAD, whose `_KIND_ORDER` (`project_upgrade.py`:539) omits Breaking, so it sorts after up to 18 capped entries
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_upgrade_breaking.py::UpgradeDigestTests::test_breaking_leads_the_digest_uncapped
- **AC3:** Given the Breaking text, then it states that entries in 6.0.0 describing plan review, the test plan, repair plans, per-unit sign-off, depth tiers or mutation evidence record machinery this release later removed. Fails on: silently deleting the 29 superseded fragments, which loses the history, or leaving them unflagged, which advertises deleted features
  - **Verify:** pytest tools/tests/test_lean_breaking_inventory.py::BreakingInventoryTests::test_superseded_entries_are_flagged

## Notes

Measured at 013a46d0: of 113 fragments, 22 Added, 45 Changed, 49 Fixed, 0 Breaking, 0 Removed; the v5.1.0-to-HEAD surface diff removes 14 verbs (autosprint.py preflight, plan_review.py check/record, repair_plan.py brief/gate, sprint.py preflight, validate.py warning-ratchet, verify_ac.py depth/depth-check/testplan and its 4 subverbs); Sprint 5's EP0263 units remove more. This is release-gate.md section 8's breaking-change inventory, written as a fragment so `release_cut.py changelog-cut` carries it rather than a hand edit at the cut. Ratchet (LC-008): AC1 is derived from the tag and the code, never a hand list; it self-retires at the 6.0.0 tag. Lands after every Sprint 5 deletion.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U1) |
