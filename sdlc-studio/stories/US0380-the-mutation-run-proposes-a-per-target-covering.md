# US0380: the mutation run proposes a per-target covering command from its own reference scan, zero out-of-selection warnings by construction, a hand --test unchanged

> **Status:** Review
> **Delivers:** CR0377
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0138
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py

## User Story

**As an** operator pointing the mutation gate at a target
**I want** a covering command derived from the run's own reference scan
**So that** a run with it has zero out-of-selection warnings by construction

## Acceptance Criteria

### AC1: given targets and no --test, or a --suggest-test flag, the run prints the derived covering command

- **Given** targets and either no --test or a --suggest-test flag
- **When** the run resolves the covering command from its reference scan
- **Then** given targets and no --test, or a --suggest-test flag, the run prints the derived covering command per target (the referencing test files its scan found), with the honest caveat that reference-scan coverage is a heuristic
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::SuggestCoveringCommandTests::test_suggests_the_referencing_tests_with_the_heuristic_caveat
- **Verified:** yes (2026-07-24)

### AC2: a run executed with the derived command produces zero out-of-selection warnings for its targets, by

- **Given** a run executed with the derived covering command
- **When** its selection warnings are computed
- **Then** a run executed with the derived command produces zero out-of-selection warnings for its targets, by construction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::SuggestCoveringCommandTests::test_a_run_with_the_derived_command_has_zero_out_of_selection_warnings
- **Verified:** yes (2026-07-24)

### AC3: the hand-supplied --test path is unchanged and remains the default

- **Given** a run with a hand-supplied --test command
- **When** the run executes
- **Then** the hand-supplied --test path is unchanged and remains the default
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::SuggestCoveringCommandTests::test_the_hand_supplied_test_path_is_unchanged_and_default
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
