# US0929: The PRD describes the lean product and lists the outcomes a Sprint Goal can serve

> **Status:** Draft
> **Depends on:** US0927 - the PRD Outcomes section the trace reads (CR0594 refinement)
> **Delivers:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/US0929.md
> **Epic:** EP0264
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** Maya Okafor, reading the PRD to decide what the next sprint is for
**I want** the PRD to describe the product as it runs now and to list numbered outcomes a Sprint Goal can name
**So that** the requirements are the thing a goal is traced to, not a description of a loop the code retired - End goal 4, "Keep specs, code, and tests in sync so the documentation never quietly drifts from reality"

## Acceptance Criteria

- **AC1:** Given `sdlc-studio/prd.md` after the refresh, when S1's outcome reader parses it, then it returns at least one outcome and every outcome cites a persona card and an End goal number that exist in `sdlc-studio/personas/` (Maya Okafor 1-4, Jonah Reyes 1-3); a PRD with no parseable `## Outcomes` section, or an outcome citing an End goal the card does not have, fails it
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRefreshTests::test_every_outcome_traces_to_a_real_end_goal
- **AC2:** Given the refreshed PRD, then its Mission and §4 Core Behaviours describe the delivery loop as the code runs it - a Sprint Goal of 20 words or fewer that traces to an outcome, one plan approval, one reviewer per unit with at most two rounds and carried known issues, persona rulings through `decisions.py rule`, the one-page sprint report, and failure classes in `sdlc-studio/lessons.jsonl` - and every `<script>.py <subcommand>` those two sections name appears in that script's `--help`; a section naming a subcommand that does not exist fails it
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRefreshTests::test_the_loop_section_names_only_commands_that_exist
- **AC3:** Given the refreshed PRD, then it no longer presents the retired learning loop as current: the phrases "a learning loop that must produce work" and "lifted into the store the next `sprint plan` prints unasked" are gone, and the Learning loop row of the Feature Inventory names failure classes; the test is red against today's PRD
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRefreshTests::test_the_retired_learning_loop_is_not_described_as_current

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Product seat | Groomed from CR0594's refinement: user story and criteria authored |
