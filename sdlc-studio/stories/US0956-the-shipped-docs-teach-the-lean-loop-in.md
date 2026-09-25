# US0956: The shipped docs teach the lean loop in one place

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/getting-started.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/retro.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py, changelog.d/US0956.md
> **Epic:** EP0266
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who drives a sprint through an agent that reads the skill's docs
**I want** one canonical description of the lean loop, with the command for each step, that every other doc links to
**So that** the agent follows the loop the code runs, not one of five remembered versions

## Acceptance Criteria

- **AC1:** Given `reference-sprint.md#the-loop`, then it lists, in order, plan and approve, build, review (one reviewer, at most the round cap, carried at the cap), close, sign and learn, and each step names a command present in `reference-scripts-surface.md`. Fails on: HEAD's loop (a tranche audit, a triage STOP and 'Reject -> repair')
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_the_loop_lists_its_steps_in_order_and_each_resolves
- **AC2:** Given help/sprint.md, help/getting-started.md and README.md, then each links `reference-sprint.md#the-loop` and none enumerates a loop with a different step list. Fails on: help/sprint.md keeping its own step list (back-to-basics defect 16: five docs gave five loop lengths)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_there_is_one_canonical_loop
- **AC3:** Given reference-review.md, then it states the review round cap as the value `critic`'s shipped default holds and what carrying a unit at the cap means. Fails on: a hand-typed '2' that the test does not read from `critic.DEFAULT_REVIEW_CEILING`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_the_review_cap_matches_the_code
- **AC4:** Given help/retro.md, then it shows the Keep, Stop and Try shape and the Try limit `retro.py validate` enforces. Fails on: HEAD, where no shipped doc names Keep, Stop and Try
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_the_retro_help_matches_the_validator

## Notes

- Depends on: US0924
- US0924 removes the retired prose from these files; this unit adds the positive teaching, so it lands after US0924. Measured at 013a46d0: grep finds no shipped help or reference naming Keep/Stop/Try, and the two-round cap appears only in templates/audit-profiles/skill.md.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U5) |
