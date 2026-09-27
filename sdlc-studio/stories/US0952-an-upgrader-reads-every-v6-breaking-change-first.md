# US0952: An upgrader reads every v6 breaking change first

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** changelog.d/US0952.md, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_upgrade_breaking.py, tools/tests/test_lean_breaking_inventory.py, tools/check_links.py, tools/tests/test_check_links.py
> **Epic:** EP0266
> **Points:** 3
> **Persona:** Jonah Reyes

## User Story

**As a** team lead upgrading a project from v5.1 to v6
**I want** the changelog and `project upgrade` to show the breaking changes first, each with what I must do
**So that** I act on the removed verbs, flags and keys before they refuse my scripts or CI

## Acceptance Criteria

- **AC1:** Given the 6.0.0 Breaking text (the `<!-- section: Breaking -->` fragment `changelog.d/US0952.md` before the cut; the `### Breaking` block under `## [6.0.0]` after the cut renames today's section `## [6.0.0-rc.1]`), then it opens by telling a 5.1 upgrader that every breaking change listed under 6.0.0-rc.1 ships in 6.0.0, links that section, and says to run `migrate` then `migrate --apply`; and every verb in `migrate._retired_verbs()`, every key in `sdlc_md.RETIRED_CONFIG_KEYS` and every id in `sdlc_md.RETIRED_CHECK_IDS` appears in the Breaking text of 6.0.0 or 6.0.0-rc.1. Fails on: the cut's rename alone, which leaves `## [6.0.0]` holding only Sprint 6's fixes, so a reader of the 6.0.0 section sees no breaking change at all; a verb or key retired during Sprint 6 with no Breaking line
  - **Verify:** pytest tools/tests/test_lean_breaking_inventory.py::BreakingInventoryTests::test_every_registered_retirement_is_disclosed
  - **Verified:** yes (2026-09-27)
- **AC2:** Given a fixture CHANGELOG with `[6.0.0]` (1 Breaking, 7 Added, 7 Changed, 7 Fixed) above `[6.0.0-rc.1]` (4 Breaking) above `[5.1.0]`, when `project_upgrade` renders its digest for a project recorded at 5.1.0 and installed at 6.0.0, then the Breaking group prints first with all 5 entries, uncapped; and for a project recorded at 6.0.0-rc.1, only 6.0.0's entries appear. Fails on: HEAD, whose `_KIND_ORDER` (project_upgrade.py:539) omits Breaking so it prints after up to 18 capped entries, and whose `_VER_HEAD_RE` does not read a pre-release heading, so rc.1's entries are folded into 6.0.0's and shown again to a project already on rc.1
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_upgrade_breaking.py::UpgradeDigestTests::test_breaking_leads_the_digest_uncapped
  - **Verified:** yes (2026-09-27)
- **AC3:** Given the 6.0.0 Breaking text, then it states that entries under 6.0.0-rc.1 adding or fixing plan review, the test plan, repair plans, per-unit sign-off, depth tiers or mutation evidence describe machinery the same release then removed, and that the Breaking tables are the current word. Fails on: leaving them unflagged (the rc.1 section's Added, Changed and Fixed name that machinery on 84 lines, among them 'The repair-plan gate is reachable'), or deleting them, which loses the history
  - **Verify:** pytest tools/tests/test_lean_breaking_inventory.py::BreakingInventoryTests::test_superseded_entries_are_flagged
  - **Verified:** yes (2026-09-27)
- **AC4:** Given a root doc linking `CHANGELOG.md#<anchor>`, when `tools/check_links.py` runs, then an anchor no CHANGELOG heading produces exits non-zero naming the doc, the line and the anchor, and one that resolves passes. Fails on: HEAD's root-docs pass, which checks the file only, so the cut's rename silently breaks the rc.1 notes' two `#600---2026-09-26` links (lines 45 and 135) and nothing notices
  - **Verify:** pytest tools/tests/test_check_links.py::RootDocAnchorTests::test_a_changelog_anchor_that_resolves_nowhere_fails
  - **Verified:** yes (2026-09-27)

## Notes

Measured at 013a46d0: of 113 fragments, 22 Added, 45 Changed, 49 Fixed, 0 Breaking, 0 Removed; the v5.1.0-to-HEAD surface diff removes 14 verbs (autosprint.py preflight, plan_review.py check/record, repair_plan.py brief/gate, sprint.py preflight, validate.py warning-ratchet, verify_ac.py depth/depth-check/testplan and its 4 subverbs); Sprint 5's EP0263 units remove more. This is release-gate.md section 8's breaking-change inventory, written as a fragment so `release_cut.py changelog-cut` carries it rather than a hand edit at the cut. Ratchet (LC-008): AC1 is derived from the tag and the code, never a hand list; it self-retires at the 6.0.0 tag. Lands after every Sprint 5 deletion.

- 2026-09-27 re-measure (product seat, dee380d9): the inventory the old AC1 asked for already exists. The rc.1 release commit (6ca07a98) wrote it by hand under `## [6.0.0]` from seven derived sources: 58 entries (19 verbs, 20 flags, 11 retired keys and 2 changed defaults, 2 check ids, 4 gate lanes). What is still true: the cut renames that heading `[6.0.0-rc.1]` (operator ruling 4), so without this unit the 6.0.0 section a 5.1 reader opens has no Breaking block; the digest still sorts Breaking last and capped; nothing flags the rc.1 section's entries for machinery the same release removed; and the rename breaks two anchors no guard reads. AC1 is re-anchored on the post-cut layout, AC4 is new (+1 point).
- Depends on BG0790: AC2's rc.1 case needs pre-release ordering, and both edit `project_upgrade.py`; land BG0790 first.
- Ratchet (LC-008): AC1 checks the registries against the Breaking text (release-gate section 8 is a checklist item, not a name census, and is left as it is); AC4 widens check_links' existing root-docs pass to CHANGELOG anchors rather than adding a lane (scoped to CHANGELOG anchors: other root-doc anchors are not measured and could surface pre-existing breaks).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U1) |
| 2026-09-27 | sdlc-studio v6 planning | Product seat, Sprint 6 re-measure at dee380d9: 2 -> 3 points; the inventory exists (rc.1), so AC1 re-anchors on the post-rename layout and derives from the registries; AC2 adds the pre-release heading case; AC4 new: check_links resolves CHANGELOG anchors |
| 2026-09-27 | sdlc | Notes: the claim that AC1 retires a hand census in release-gate section 8 is withdrawn; that section is a checklist item, not a name census (review round 1) |
