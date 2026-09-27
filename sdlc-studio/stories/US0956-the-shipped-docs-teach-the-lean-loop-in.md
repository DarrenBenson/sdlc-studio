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

- **AC1:** Given `reference-sprint.md#the-loop`, then it lists, in order, plan and approve, build, review (one reviewer, at most the round cap, carried at the cap), close, sign and learn, and each step names a command present in `reference-scripts-surface.md`. Fails on: HEAD's loop (76-328): step 2 'Tranche audit', step 3 'Clarify + Triage STOP', 'Reject -> repair', a mandatory `mutation.py run` before the retro gate (181) and a full-diff adversarial critic pass at the close
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_the_loop_lists_its_steps_in_order_and_each_resolves
- **AC2:** Given help/sprint.md and help/getting-started.md, then each links `reference-sprint.md#the-loop` and neither enumerates a loop with a different step list. Fails on: help/sprint.md keeping its own step list (back-to-basics defect 16: five docs gave five loop lengths)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_there_is_one_canonical_loop
- **AC3:** Given reference-review.md, then it states the review round cap as the value `critic.DEFAULT_REVIEW_CEILING` holds (critic.py:1445, overridable by `review.max_rounds`) and what carrying a unit at the cap means. Fails on: HEAD's hand-typed '2' (reference-review.md 464), which the test does not read from the code
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_the_review_cap_matches_the_code
- **AC4:** Given help/retro.md, then it shows the Keep, Stop and Try shape and the Try limit `retro.TRY_MAX` holds (retro.py:99). Fails on: HEAD, where only templates/reviews/retro.md names Keep, Stop and Try and no help does
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_loop_docs.py::LoopDocTests::test_the_retro_help_matches_the_validator

## Notes

- Depends on: US0924
- US0924 removes the retired prose from these files; this unit adds the positive teaching, so it lands after US0924. Measured at 013a46d0: grep finds no shipped help or reference naming Keep/Stop/Try, and the two-round cap appears only in templates/audit-profiles/skill.md.
- - 2026-09-27 re-measure (product seat, dee380d9): premises hold. README.md leaves AC2: this unit's Affects never held README, which US0954 owns whole, so US0954 AC2 now carries the README's link to the loop. Depends on US0924, which clears the retired lines from reference-sprint.md, help/sprint.md and reference-review.md first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U5) |
| 2026-09-27 | sdlc-studio v6 planning | Product seat, Sprint 6 re-measure at dee380d9: README leaves AC2 for US0954; Fails-on lines re-measured and the cap and Try limit anchored to their constants; points stay 5 |
