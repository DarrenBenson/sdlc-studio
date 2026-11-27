# US1346: sprint lane brief tells a builder whose unit takes a solution review to write its approach note first and stop

> **Status:** Ready
> **Risk-class:** high
> **Delivers:** CR0756
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_lane_brief.py, changelog.d/US1346.md
> **Epic:** EP0385
> **Points:** 2
> **Depends on:** US1344
> **Persona:** Abena Osei

## User Story

**As** a builder in a lane, **I want** my brief to say when my unit takes a solution review and
what to hand in first, **so that** I do not write code before the plan is agreed.

## Acceptance Criteria

### AC1: a unit the setting names is told to write its note first, and an unnamed one is not

- **Given** a project setting `review.solution_review.min_points: 2`, a 3-point story and a
  1-point story, and no note or verdict for either
- **When** `sprint.py lane brief --units <id>` is run for each
- **Then** the 3-point brief, before its build steps, names the reason (3 points, at or above
  `review.solution_review.min_points` 2), the note's path `sdlc-studio/.local/lane/<id>-approach.md`
  and its five headings, and tells the builder to write HANDOFF.md saying the approach awaits
  review, stage nothing and hand back HANDOFF; the 1-point brief carries no solution review line.
  Fails on: HEAD, whose brief for a 3-point unit under that setting has 0 lines naming an
  approach note or a solution review.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_lane_brief.py::SolutionReviewLaneBriefTests::test_a_named_unit_is_told_to_write_its_note_first

### AC2: the brief follows the recorded verdict

- **Given** the 3-point story with a note, then a CHANGES verdict recorded against it, then a GO
  recorded against the revised note
- **When** the lane brief is printed after each
- **Then** after CHANGES it quotes the changes and asks for a revised note; after GO it says the
  approach is agreed, names the round and the digest, tells the builder to build to it, and says
  that editing the note voids the GO. Fails on: HEAD, where nothing in sprint.py reads a solution
  review.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_lane_brief.py::SolutionReviewLaneBriefTests::test_the_brief_follows_the_recorded_verdict

### AC3: the note is named in the hand-in list by the unit's key

- **Given** the 3-point story, and a schema-3 project with a hyphenated story id
- **When** the lane brief is printed, and `lanes.approach_hand_in_name` is called for each id
- **Then** the hand-in list names `<key>-approach.md` beside the claims and mutants files, keyed
  as `lanes.hand_in_names` keys them for both ids. Fails on: HEAD, where lib/lanes.py has 0
  mentions of an approach and the hand-in list names four files.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_lane_brief.py::SolutionReviewLaneBriefTests::test_the_note_is_named_by_the_unit_key

## Notes

- Ran: `sprint.py lane brief --units US0101` in a fixture with `min_points: 2` and a 3-point
  story: exit 0, 68 lines, 0 matches (Evidence S3).
- HANDOFF is the builder agent definition's own outcome word (`.claude/agents/sdlc-builder.md`:
  DONE, BLOCKED or HANDOFF), so the definition does not change; `test_agent_definitions` pins
  its three-line hand-back sentence.
- Beside the existing tests: lib/lanes.py is read by 27 modules, sprint.py by 208.
  test_lane_builder_brief and test_lean_lane_brief_repair_scope assert specific lines of the
  brief and its hand-in list, never its length, so an added step for a named unit holds; the
  unnamed control keeps every existing brief unchanged.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | orchestrator (D0545) | Groomed: criteria with Fails on run at HEAD and Verify nodes, from the engineering seat's draft; default and this repository's setting per D0647 (product seat). |
