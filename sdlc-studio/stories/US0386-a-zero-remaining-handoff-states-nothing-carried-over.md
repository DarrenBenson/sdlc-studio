# US0386: a zero-remaining handoff states nothing carried over, non-zero unchanged, two-sided tests

> **Status:** Draft
> **Delivers:** CR0386
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0142
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py

## User Story

**As a** operator running sprint plan after a clean close
**I want** the handoff line to say nothing carried over when there is nothing outstanding
**So that** a clean handoff reads as good news rather than a false action item above the warnings that need reading

## Acceptance Criteria

### AC1: a zero-remaining handoff states nothing carried over

- **Given** the last run closed with 0 remaining items
- **When** sprint plan prints the handoff line
- **Then** it states that nothing carried over and offers no `--worklist` command
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py::HandoffLine::test_zero_remaining_states_nothing_carried_over

### AC2: a non-zero handoff is unchanged

- **Given** the last run left 1 or more remaining items
- **When** sprint plan prints the handoff line
- **Then** the existing line is unchanged, naming the count and the worklist path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py::HandoffLine::test_nonzero_remaining_names_count_and_worklist

### AC3: the boundary is pinned two-sided

- **Given** the boundary between zero and one remaining item
- **When** the tests run
- **Then** both the zero-case suppression and the non-zero retention are asserted in one test, so a future change cannot make the zero case reappear or suppress the non-zero one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py::HandoffLine::test_boundary_pinned_both_sides

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
