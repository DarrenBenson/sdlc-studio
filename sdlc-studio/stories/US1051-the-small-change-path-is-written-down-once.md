# US1051: The small-change path is written down once, and every step is a runbook command that runs end to end

> **Status:** Draft
> **Delivers:** CR0626
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_small_change_runbook.py, changelog.d/US1051.md
> **Epic:** EP0286
> **Points:** 5
> **Depends on:** US1047, US1048, US1049, US1050, BG1009
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer deciding whether a fix needs a sprint
**I want** one page that says what the small path keeps, what it skips and what rules a change out, with each step a runbook command
**So that** my agent follows a written path instead of running the whole loop or improvising a fast-track

## Acceptance Criteria

- **AC1:** Given the runbook's small-change table, when the test runs each command it names in order against a fixture bug, filling only the placeholders and making the fixture's own test and fix edits between the steps, then the bug goes from Open to Fixed with an independent verdict recorded, no run record or report is written, and `close_owed.py detect` reports nothing owed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_runbook.py::SmallChangeRunbookTests::test_the_runbook_table_runs_a_bug_to_fixed_end_to_end
- **AC2:** Given the small-change section of reference-sprint.md, when its list of disqualifiers is compared with the set `small_change.py` publishes, then each names exactly the other's members.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_runbook.py::SmallChangeRunbookTests::test_the_page_and_the_command_name_the_same_disqualifiers
- **AC3:** Given a batch of one unit that the small-change check passes, when `sprint.py plan` previews it, then it prints that the unit qualifies for the small-change path, with the `small_change.py start` command for it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_runbook.py::SmallChangeRunbookTests::test_plan_names_the_small_path_for_a_qualifying_single_unit

## Notes

- Release: 6.2 (D0355 breakdown G12, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the table omits `small_change.py start`, so revert-check has no base and the transition refuses; or a row names a flag its script does not accept.
- AC2 must fail on: a disqualifier is added to the command and not to the page, or the reverse.
- AC3 must fail on: plan prints nothing about the path, so an agent reaching for the full loop is never told it can skip it.
- reference-sprint.md gains a section, `{#small-change}`. The path keeps:
- - a single unit with an executable criterion;
- - that criterion shown failing at base with `verify_ac.py revert-check`;
- - an independent review at the derived tier, through `critic.py brief` and `critic.py record`;
- - the terminal transition, which holds both the review and the boundary.
- It skips the run, the goal review, the report, the retro and the signature. The page also says that the path reviews at the derived tier, not the CR's 'light-tier' wording; that its findings reach no lessons pass; that a run awaiting signature shuts the path meanwhile; and that for a bug only the globs and `review.spec_paths` are protected surfaces.
- The runbook gains a section, '0. A small change, outside a run'. In order: `file_finding.py file` or `artifact.py new`, `small_change.py check` then `start`, `verify_ac.py run` (red, then green), `verify_ac.py revert-check`, `critic.py brief`, `critic.py record`, then `transition.py set`. Each row carries the hand-rolled shape it replaces. The review step warns that revert-check rewrites the live tree until BG1014 lands.
- Docs-only changes stay on the path (panel answer Q7). revert-check reverts no markdown and, after BG1009, reports `not judged`. The reviewer shows the criterion failing by running it at the recorded base (doctrine 21); the author's own red run is not enough alone.
- The new runbook heading already prints in every `sprint plan`, because `render_runbook_pointer` (sprint.py:2474) prints each `##` heading. AC3's targeted line is still worth having, and it is the first thing to cut if points are tight.
- SKILL.md's loading guide gains one pointer line where an agent decides to reach for `sprint`; it stays inside the router's line budget.
- AC1 is CR0626's second criterion made executable. The test reads the table, not a copy of it, and expects the post-BG1009 revert-check verdicts.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G12 after the refine panel's review |
