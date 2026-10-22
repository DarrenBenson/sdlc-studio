# US1093: sprint.py lane brief hands a fresh builder agent everything it needs to build one unit (its Affects, criteria, author self-check, seat card and the commit and Verify commands), and the runbook builds each unit that way

> **Status:** Ready
> **Delivers:** CR0651
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1093.md
> **Epic:** EP0292
> **Points:** 5
> **Depends on:** US1088
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, leaving the loop to drive a batch while she is away
**I want** each unit built by a fresh agent from one printed brief, with the orchestrating context holding only the run state and the verdicts and waiting on each builder's completion notification
**So that** the orchestrator's context stays small, so each turn re-reads a few thousand tokens rather than half a million, and the batch costs what its units cost

## Acceptance Criteria

- **AC1:** Given an open run whose batch holds a groomed story, when `sprint.py lane brief --units <id>` runs, then stdout carries the unit's Affects, one path per line, equal to `sdlc_md.affects_files` of the unit, and a commit step that stages exactly those paths (`git add -- <path> ...`) and names the unit id for the commit subject
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_brief_names_the_affects_and_stages_only_them
- **AC2:** Given the same unit, then stdout carries `critic.author_self_check(root, <id>)` verbatim, then the self-check record command (`critic.py self-check record --unit <id>`) and the command that runs the unit's criteria (`verify_ac.py run --id <id>`); when `author_self_check` is replaced in-process the brief changes with it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_brief_carries_the_self_check_and_the_commands_for_this_unit
- **AC3:** Given a project seat card declaring `role: engineering` beside the shipped default, then the brief names the card that `persona_resolve.resolve_card(root, "engineering", render="build")` returns, as the work render to adopt; with no project card it names the shipped default
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_brief_names_the_engineering_seats_work_render
- **AC4:** Given `reference-sprint-toolchain.md`'s `## 3. Deliver a unit` table, when its rows are read from the source as (Do, Command, Instead of) cells, then it holds the three rows the test declares, compared cell for cell: build a unit (`sprint.py lane brief --units <id>`, handed to a fresh agent; instead of building it in the orchestrating context), wait for the builder (its completion notification; instead of polling its output or sleeping), and accept its return (`sprint.py lane return --units <id>`; instead of reading the builder's diff or transcript into the orchestrating context); the build row's Command cell also names the fallback for a harness without subagents: a fresh session per unit, started from the same brief
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderRunbookTests::test_the_deliver_table_builds_each_unit_in_a_fresh_agent

## Notes

- Serves: Maya Okafor, End goal 3.
- AC1 must fail on: the Affects popped from the brief before rendering, as `lane_dispatch` does today; `git add -A` or `git commit -a`, which sweeps a concurrent lane's files into this unit's commit
- AC2 must fail on: the self-check steps retyped in sprint.py, so they drift from what the reviewer is told; either command carrying another unit's id
- AC3 must fail on: the shipped default's path hard-coded, which shadows the project's own seat; the review render named
- AC4 must fail on: a row missing; a Command cell naming another command; the rule stated as prose under the table, which no test can compare exactly (RETRO0135)
- D0389 (4)'s push cadence is this repository's, and is left out of the shipped runbook.
- Overlap: id: US1088; relation: dependency: AC2 names the command US1088 adds, which does not exist in critic.py today; evidence: AC1: 'when `critic.py self-check record --unit <id> --claims <file> --mutants <file>` runs, then the record is written'
- Overlap: id: CR0650; relation: reused, not superseded: E2 prints the self-check CR0650 part (2) put on `critic.py brief`'s stderr (US1087); evidence: Title: 'The author's self-check is a step the tools run and require, not a rule an agent remembers'
- Overlap: id: US1019; relation: same surface (`sprint.py lane`, the toolchain runbook); a seam, not a duplicate - it changes `lane return`, E2 changes `lane brief`; evidence: AC1: 'when `sprint.py lane return --units <id>` runs, then it exits 1 as blocked'; Affects include reference-sprint-toolchain.md
- Overlap: id: CR0639; relation: related: a builder in an isolated worktree has the same lifetime question as a reviewer; not superseded; evidence: Title: 'A worktree-isolated reviewer that REJECTs cannot be resumed for its round 2 once its worktree is removed'
- Risk: Reuse, not invention: `sprint.py lane brief` already prints the criteria with their Verify lines, TRD constraints, seams, the files' history, proof owed, obligations and build lessons, and help/sprint.md:530 already tells an orchestrator to call it before dispatching. What it lacks is the Affects (popped at sprint.py:2640), the self-check, the seat card and the commands.
- Risk: Seam with E1: `sprint lane return --tokens N` records a builder's own total. Once E1 reads subagent transcripts, the runbook must not tell the orchestrator to pass it for a harness-recorded builder, or the run counts the builder twice.
- Risk: The commit message convention is the consuming project's, so the brief names the paths to stage and the unit id only; this repo's `type(ID): subject` shape is not imposed.
- Risk: Existing lane-brief tests (tests/test_lean_lane_*.py) pin parts of the text and may need their fixtures updated; and CR0640 warns a reference page edited without regenerating its reading guide fails only at push.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
