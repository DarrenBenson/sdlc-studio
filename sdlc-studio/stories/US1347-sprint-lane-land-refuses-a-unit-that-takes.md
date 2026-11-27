# US1347: sprint lane land refuses a unit that takes a solution review without an agreed approach

> **Status:** Ready
> **Risk-class:** elevated
> **Delivers:** CR0756
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_land.py, changelog.d/US1347.md, sdlc-studio/.config.yaml
> **Epic:** EP0385
> **Points:** 3
> **Depends on:** US1344, US1345, US1346
> **Persona:** Abena Osei

## User Story

**As** an engineering lead, **I want** a unit that should have had its approach agreed to be
refused at land when it was not, **so that** the step cannot be skipped by a builder or an
orchestrator in a hurry.

## Acceptance Criteria

### AC1: no note refuses the land before anything moves

- **Given** a project setting `review.solution_review.min_points: 2` and a lane worktree holding
  a 3-point story's staged work, claims and mutants, and no approach note
- **When** `sprint.py lane land --worktree <wt> --units <id>` is run
- **Then** it exits 2 naming the unit, the missing note's path and `sprint.py lane brief --units
  <id>`, main does not move, nothing is committed and the worktree stays. Fails on: HEAD, which
  landed two 3-point units with no notes under that setting, exit 0, main fast-forwarded.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_land.py::SolutionReviewLandTests::test_no_note_refuses_the_land_before_anything_moves

### AC2: a land without a current GO is refused, naming why

- **Given** the same worktree with a note, three times: with no verdict recorded, with CHANGES
  the latest verdict, and with a GO recorded against an earlier text of the note
- **When** the land is run each time
- **Then** each exits 2 before anything moves, naming respectively that no solution review is
  recorded (with `critic.py approach brief`), the CHANGES round, and the GO's digest beside the
  note's digest now. Fails on: HEAD, where lib/lanes.py reads no solution review.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_land.py::SolutionReviewLandTests::test_a_land_without_a_current_go_is_refused

### AC3: an agreed approach lands, and an unnamed unit lands as before

- **Given** the 3-point story with a GO bound to its current note, and a 1-point story the
  setting does not name, with no note
- **When** both are landed
- **Then** both land; the 3-point unit's output carries one line naming its GO, round and
  digest, and the 1-point unit's output carries no solution review line. Fails on: HEAD, whose
  land output names no solution review for any unit.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_land.py::SolutionReviewLandTests::test_an_agreed_approach_lands_and_an_unnamed_unit_lands_as_before

### AC4: the runbook and the sprint help say what land refuses

- **Given** reference-sprint-toolchain.md and help/sprint.md
- **When** they are read
- **Then** the runbook's land row says it refuses a unit the setting names that has no agreed
  approach, still saying it removes the worktree, and the Lanes section of help/sprint.md names
  the setting, the note, `critic.py approach brief`, `critic.py approach record` and the
  refusal. Fails on: HEAD, where both pages have 0 mentions of a solution review.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_land.py::SolutionReviewLandTests::test_the_runbook_and_the_sprint_help_say_what_land_refuses

## Notes

- Ran: a two-worktree land in a fixture with `min_points: 2` and two 3-point stories, no notes:
  exit 0, `main fast-forwarded to f7e8762`, both worktrees removed (Evidence S4).
- Put the check in `_preflight`, so it refuses through `LandError` with the other preflight
  refusals and a multi-unit land refuses whole, as it does now.
- A test land takes tens of seconds; give the module's subprocess calls the 600-second timeout
  test_lane_land uses, and build the fixture as test_lane_land's `_LaneFixture` does.
- help/sprint.md is in an unbudgeted tree (`check_budgets.UNBUDGETED_TREES`); it is read by 17
  modules, which pin other passages (drive, handoff, delegated minutes); add one paragraph to the
  Lanes section. US1294 and US1342 also edit this page.
- D0647 (product seat): the refusal message and help/sprint.md also say that the headless flows (`sprint drive`, `lane run`) do not take the step yet, and that a unit committed in the orchestrator's own tree is not checked.
- Turn the step on for this repository in this story's commit: `review.solution_review.min_points: 3` and `risk_classes: [high]` in sdlc-studio/.config.yaml (D0647).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | orchestrator (D0545) | Groomed: criteria with Fails on run at HEAD and Verify nodes, from the engineering seat's draft; default and this repository's setting per D0647 (product seat). |
