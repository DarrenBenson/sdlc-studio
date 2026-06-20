# US0027: code plan complexity estimation + refactor-first

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0029, RFC0009)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** implementer planning a story
**I want** the plan's estimate weighted by the touched code's complexity, with a
refactor-first recommendation for hotspots
**So that** a change in difficult code is sized honestly and made easy before it is made
(RFC0009 WS2). Advisory, never a gate.

## Acceptance Criteria

### AC1: High-complexity blast radius -> high difficulty + refactor-first

- **Given** a change touching a deeply-nested function over the threshold
- **When** `assess` runs
- **Then** `difficulty` is `high` and a refactor-first line names the hotspot
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::AssessTests::test_hotspot_drives_high_difficulty_and_refactor_first
- **Verified:** yes (2026-06-20)

### AC2: Simple change -> low, no recommendation

- **Given** a change touching only a trivial function
- **When** `assess` runs
- **Then** `difficulty` is `low` and `refactor_first` is empty
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::AssessTests::test_simple_change_is_low_with_no_refactor_first
- **Verified:** yes (2026-06-20)

### AC3: Advisory - never blocks

- **Given** a high-complexity change
- **When** `assess` CLI runs
- **Then** it prints the refactor-first guidance and exits 0
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::AssessTests::test_recommendation_is_advisory_exit_zero
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/complexity.py`: `assess(repo_root, files, threshold)` + `assess` CLI.
`reference-code.md` code-plan step 6b folds difficulty + refactor-first into the plan.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0029) | Decomposed from CR0029 / RFC0009 WS2; critic APPROVE |
