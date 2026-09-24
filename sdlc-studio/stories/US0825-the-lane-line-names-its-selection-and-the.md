# US0825: the lane line names its selection and the rule that produced it, so a narrowed lane is never read as a full one

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Delivers:** CR0586
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0253
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the lane line names its selection and the rule that produced it, so a narrowed lane is never read as a full one
**So that** CR0586 is delivered by work that can be planned and checked

## Acceptance Criteria

A narrowed lane that reports like a full one is worse than either: the reader cannot tell which ran. Every persona raised this independently.

### AC1: the line names what ran, what was skipped, and the rule that decided

- **Given** a push selecting 11 of 133 modules
- **When** the lane reports
- **Then** its detail carries the selected count against the total, the base sha the diff used, and the rule's name, so `[PASS] module-alone` can never be read as the full sweep
- **Mutant:** print the selected count alone - 11 modules green reads identically whether the other 122 were skipped or never existed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneSelectionTests::test_the_line_names_the_selection_and_its_rule

### AC2: the full sweep says so in the same field a reader already looks at

- **Given** a release boundary or a push whose base could not be resolved
- **When** the lane reports
- **Then** the same field reads that every module ran and why, rather than omitting the selection clause
- **Mutant:** omit the clause when nothing was narrowed - absence then means both "full sweep" and "an older build that could not narrow"
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneSelectionTests::test_a_full_run_states_that_it_was_full

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - US0881 |
