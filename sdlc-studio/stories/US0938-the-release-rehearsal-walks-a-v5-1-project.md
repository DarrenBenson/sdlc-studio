# US0938: The release rehearsal walks a v5.1 project across to v6, and every known gap it tolerates has an open owner

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/rehearse-release.sh, tools/release-rehearsal-baseline.txt, .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py, sdlc-studio/bugs/BG0149-artifact-py-silently-drops-points-on-a-story.md, changelog.d/US0938.md
> **Epic:** EP0265
> **Points:** 3
> **Persona:** Jonah Reyes

## User Story

**As a** team lead upgrading a v5.1 project to v6
**I want** the release rehearsal to build a workspace in the v5.1 shape, migrate it and gate it, as it already does for a v4-era one
**So that** the path every existing v5 user takes into v6 is proven before the tag, not discovered in their repository

## Acceptance Criteria

- **AC1:** Given `rehearse-release.sh upgrade-v5`, when it builds a workspace in the v5.1 shape (schema 3, a Definition of Done tagging `[check: review.two-role]` and `[check: repair.mutation-evidence]`, an AGENTS.md naming `review.two_role_after`) and runs `migrate --apply` then `gate.py`, then it exits 0 only when the DoD carries no retired tag, migrate's report names the AGENTS.md line, and the gate's failing lanes match the baseline. Fails on: HEAD's migrate, which leaves both tags (measured on a v5.1.0 `init` project); a harness that drops `--apply`, which the tag assertion catches
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py::UpgradeRehearsalTests::test_the_v5_upgrade_strips_retired_tags
  - **Verified:** yes (2026-09-26)
- **AC2:** Given `rehearse-release.sh all`, then it runs greenfield, upgrade and upgrade-v5, in that order, so the release-rehearsal gate lane covers the v5 path. Fails on: adding the mode but leaving `all` as it was, so the release boundary never runs it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py::UpgradeRehearsalTests::test_all_runs_the_v5_path
  - **Verified:** yes (2026-09-26)
- **AC3:** Given `tools/release-rehearsal-baseline.txt`, when the harness reports its known gaps, then each row's clearing artefact is an open artefact. Fails on: HEAD's conformance row, which names CR0497, Rejected, so the tolerated gap has no owner
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py::UpgradeRehearsalTests::test_every_baselined_gap_names_an_open_owner
  - **Verified:** yes (2026-09-26)
- **AC4:** Given `known_issues.py bar`, then it names no finding whose severity is in neither the barred nor the disclosed set. Fails on: BG0149 left at severity `major` (measured warning at HEAD)
  - **Verify:** shell sh -c '! python3 tools/known_issues.py bar 2>&1 | grep -q "in neither"'
  - **Verified:** yes (2026-09-26)

## Notes

- Depends on: US0925
- Wave 5, after US0925 (the migrate that strips the tags). The owner for the conformance row is chosen or filed (via `file_finding.py`) by this unit; the row itself stays until that owner clears it. The open-owner check extends the existing `test_every_baselined_lane_names_the_artefact_that_clears_it` rather than adding a lane; its measured yield is the one ownerless row at HEAD (LC-008). No consuming project on this machine is on v5.x (one on 4.1.0, one on 3.1.0, one on 2.4.1), so the fixture is the only v5.1 witness; the rc.1 soak rehearses a consuming project and a consuming project from copies.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (NEW-B) |
