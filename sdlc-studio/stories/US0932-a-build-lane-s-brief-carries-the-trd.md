# US0932: A build lane's brief carries the TRD constraints of the components its unit touches

> **Status:** In Progress
> **Depends on:** US0933 - both edit the TRD Component Overview table (CR0594 refinement)
> **Delivers:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, sdlc-studio/trd.md, .claude/skills/sdlc-studio/templates/core/trd.md, .claude/skills/sdlc-studio/reference-trd.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_trd_constraints.py, tools/tests/test_lean_trd_constraints_repo.py, changelog.d/US0932.md
> **Epic:** EP0264
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** Maya Okafor, who keeps a TRD so the agent respects the architecture
**I want** the constraints the TRD records for a component handed to the agent building a unit that touches it
**So that** the TRD is read where it can prevent a defect, not only kept - End goal 4, "Keep specs, code, and tests in sync so the documentation never quietly drifts from reality"

## Acceptance Criteria

- **AC1:** Given a fixture TRD whose Component Overview table has a Constraints column and rows for `` `scripts/` `` and `` `SKILL.md` ``, when `sprint.py lane brief --units <unit>` runs for a unit affecting `.claude/skills/x/scripts/a.py`, then the brief lists the `scripts/` row's component and constraint and not the `SKILL.md` row's; matching a component by substring, so that `scripts/` also matches `tools/scripts_helper.py`, fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_trd_constraints.py::TrdConstraintsTests::test_the_touched_components_constraints_reach_the_brief
- **AC2:** Given a unit whose files match no component, or a TRD with no Constraints column, or no TRD, then the brief says in one line that the TRD records no constraints for these files, and the dispatch is otherwise unchanged - no refusal; an implementation that refuses the dispatch or omits the line fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_trd_constraints.py::TrdConstraintsTests::test_no_matching_component_is_stated_not_refused
- **AC3:** Given `templates/core/trd.md`, then its Component Overview table carries the Constraints column with a placeholder, and `reference-trd.md` says the build brief reads it, so a consuming project's TRD is read the same way
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_trd_constraints.py::TrdConstraintsTests::test_the_template_carries_the_constraints_column
- **AC4:** Given this repository's `sdlc-studio/trd.md`, then each §13 Must Have constraint that governs one component sits in that component's Constraints cell, and a lane brief for a unit affecting `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` carries the constraint that `lib/sdlc_md.py` is the single source of truth for markdown conventions; a TRD left without the column fails it
  - **Verify:** pytest tools/tests/test_lean_trd_constraints_repo.py::TrdConstraintsRepoTests::test_this_repos_trd_constraints_reach_a_brief

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Product seat | Groomed from CR0594's refinement: user story and criteria authored |
