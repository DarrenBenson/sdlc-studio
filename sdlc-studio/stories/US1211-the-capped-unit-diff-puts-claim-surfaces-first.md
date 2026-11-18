# US1211: The capped unit diff puts claim surfaces first and the full diff is written beside the brief

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0679
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_diff_order.py
> **Epic:** EP0331
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The capped unit diff puts claim surfaces first and the full diff is written beside the brief
**So that** CR0679 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A cut keeps the artefact and drops tests first

- **Given** a unit whose diff over its own artefact, a changelog fragment, a reference page, a production script and a test file is longer than the tier's cap
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** the UNIT DIFF shows the files in the order artefact, changelog.d, docs, production, tests; the artefact's and the fragment's hunks are whole; and the remainder line names the test file as cut. Fails on: git's name order, in which the artefact under `sdlc-studio/` is the file the cap cuts
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_diff_order.py::BriefDiffOrderTests::test_a_cut_keeps_the_artefact_and_drops_tests_first

### AC2: The uncapped diff is written beside the brief and the remainder line names it

- **Given** the same unit, and a second unit whose diff is under the cap
- **When** `critic.py brief` is run for each
- **Then** for the first, the whole base to HEAD diff of the Affects is written to `<brief>.diff` beside the saved brief and the remainder line names that path; for the second, no `.diff` file is written and none is named. Fails on: a remainder line that names only a git command for the reviewer to run, or a `.diff` file that holds the capped text
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_diff_order.py::BriefDiffOrderTests::test_the_full_diff_is_written_beside_the_brief_and_named

### AC3: The scope line says the brief already carries the diff

- **Given** a full-tier brief that carries a UNIT DIFF, and a brief for a unit with no Affects that carries none
- **When** each brief's scope line is read
- **Then** the first says the UNIT DIFF below is base to HEAD for those paths; only the second tells the reviewer to take the diff with git. Fails on: a brief that carries the diff and still tells the reviewer to inspect the same paths with git diff
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_diff_order.py::BriefDiffOrderTests::test_the_scope_line_says_the_diff_is_base_to_head

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
