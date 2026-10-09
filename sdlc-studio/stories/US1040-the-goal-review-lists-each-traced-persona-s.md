# US1040: The goal review lists each traced persona's testable End goals and names a Sprint Goal nothing can check

> **Status:** Draft
> **Delivers:** CR0621
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py, changelog.d/US1040.md
> **Epic:** EP0285
> **Points:** 3
> **Depends on:** US1039, BG1002, US1036
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, approving a Sprint Goal
**I want** the goal review and the plan to show each traced persona's End goals with their Verify lines, and to name a goal that traces to personas with no executable check
**So that** a goal that cannot be checked is named at plan, not discovered halfway through the sprint as a bug

## Acceptance Criteria

- **AC1:** Given a traced persona whose End goal 1 carries no Verify, End goal 2 an executable Verify and End goal 3 `Verify: manual walk each room`, when `sprint.py goal-review brief --goal` runs on a goal naming that persona, then End goal 2 is listed with its Verify, End goal 3 as checked by hand and End goal 1 as not testable, each under its number as on the card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::TestableListingTests::test_brief_lists_each_end_goal_with_its_check
- **AC2:** Given a Sprint Goal that traces to one or more personas none of whose End goals carries an executable Verify, when the goal-review brief and `sprint.py plan --sprint-goal` run, then each prints one goal-check line naming those personas and saying nothing can check the goal, while the plan's exit code and batch are the same as without the line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::GoalCheckTests::test_goal_with_no_executable_end_goal_is_named_on_brief_and_plan
- **AC3:** Given a goal tracing to Maya Okafor, whose End goals carry no Verify, while an untraced persona's End goal carries one, when `sprint.py plan --format json` runs, then `goal_trace.checkable` is false, and once Maya's End goal 1 gains an executable Verify the same plan reports it true and names that goal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::GoalCheckTests::test_checkable_reads_only_the_traced_personas
- **AC4:** Given a goal that traces only to a PRD outcome, and a goal that traces to nothing, in a project whose End goals carry no Verify lines, when the goal-review brief and `sprint.py plan` run, then the outcome-only goal prints no goal-check line, and the untraced goal prints only today's single `Goal serves: NONE` line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::GoalCheckBoundaryTests::test_outcome_only_and_untraced_goals_print_no_goal_check

## Notes

- Release: 6.2 (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the brief keeps today's text-only listing, attaches a Verify to the following goal, or counts a manual Verify as testable
- AC2 must fail on: the line is missing from either surface, or the plan returns non-zero on it (advice turned refusal)
- AC3 must fail on: checkability is computed over every persona card rather than the traced personas, so an unrelated testable goal makes an uncheckable Sprint Goal read checkable
- AC4 must fail on: the goal-check line fires on an outcome-only or untraced goal, so a project with no End goal Verify lines yet sees it every sprint (the noise CR0623 complains about)
- Serves: Maya Okafor #3 (drive a batch to done, pausing only when a decision is hers).
- The rule (panel): the goal-check line fires only when the goal traces to at least one persona and none of the traced personas' End goals has an executable Verify; a manual Verify is listed as checked by hand and never counts.
- 'The batch's served personas' (CR0621's AC) are the personas the goal traces to: its wording and, after BG1002, `--serves` (panel, confirmed).
- `goal_trace` (sprint.py:10000) gains per-persona testable End goals and `checkable` (present only when the trace names a persona); `_render_goal_trace` and `_goal_served_lines` (sprint.py:11092) both render from that one record.
- Advice, never a refusal (D0266, LC-008).
- One cluster with BG1002 and G10's three CR0627 stories on `_goal_served_lines` and `_compose_seat_brief`, built in sequence: BG1002, then G10's per-seat card story (which restructures the brief), then this story. With BG1002 in, a Served-role persona such as the homelab's Household Member is listed and annotated with no further change here.
- No served-persona brief or lens is built here or in G10: the served persona reaches every seat's brief as data (these End goals, and the plan advisory's owed list).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
