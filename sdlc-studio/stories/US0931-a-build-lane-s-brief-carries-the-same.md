# US0931: A build lane's brief carries the same file history, and tells the author that history outranks an artefact's account

> **Status:** Draft
> **Delivers:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_history.py, changelog.d/US0931.md
> **Epic:** EP0264
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As** Maya Okafor, whose units come back rejected for prior art one command would have shown
**I want** the agent building a unit to see the same file history its reviewer will see, before it writes a line
**So that** the author meets the prior work and its defects at the start rather than in a REJECT - End goal 3, "Drive a whole batch of work to "done" autonomously, pausing only when a decision is genuinely hers"

## Acceptance Criteria

- **AC1:** Given S4's fixture, when `sprint.py lane brief --units <unit>` runs, then the brief carries a history section identical to the one `critic.py brief` renders for that unit, produced by the same function under the same bound; a second implementation that lists different units fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_history.py::LaneHistoryTests::test_the_lane_and_review_briefs_carry_the_same_history
- **AC2:** Given that brief, then its history section opens with the prior-art instruction: run `git log -S <symbol>` before changing a symbol you did not write; where an artefact and the history disagree, the history wins; and do not read the artefact corpus in bulk; a brief without the instruction fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_history.py::LaneHistoryTests::test_the_history_section_carries_the_prior_art_instruction
- **AC3:** Given a lane dispatch of three units, then the Done-unit corpus is walked once for the dispatch, not once per unit (a walk costs about 1.3 s on this repository); an implementation that walks per unit fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_history.py::LaneHistoryTests::test_the_corpus_is_walked_once_per_dispatch

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Product seat | Groomed from CR0594's refinement: user story and criteria authored |
