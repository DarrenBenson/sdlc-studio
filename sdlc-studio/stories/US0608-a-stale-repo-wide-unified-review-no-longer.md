# US0608: A stale repo-wide unified review no longer hard-blocks a sprint close whose own units are all covered, and is reported as cadence debt instead

> **Status:** Ready
> **Delivers:** CR0522
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0200
> **Points:** 5

## User Story

**As a** maintainer closing a fully reviewed sprint
**I want** the repo-wide periodic review to stop hard-blocking my close
**So that** a sprint does not inherit the deferral history of a ceremony it does not own

## Acceptance Criteria

### AC1: a covered batch closes with a stale unified review

- **Given** a run whose units all carry independent review coverage and sign-off, and a stale repo-wide review
- **When** the close runs
- **Then** it proceeds, because the sprint's own coverage is what the close is entitled to judge
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCadenceTests::test_a_covered_batch_closes_with_a_stale_unified_review

### AC2: an uncovered batch still refuses

- **Given** a run whose units are NOT all covered
- **When** the close runs
- **Then** it still refuses - the positive control, so this does not become a way to close an unreviewed batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCadenceTests::test_an_uncovered_batch_still_refuses

### AC3: the staleness is reported, never dropped

- **Given** the close in AC1
- **When** its output and the close-owed ledger are read
- **Then** both name the stale periodic review, so proceeding and forgetting stay different events
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCadenceTests::test_the_staleness_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
