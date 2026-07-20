# US0283: Close reports whether the outstanding set shrinks or grows across re-runs; hard correctness gates stay unwaivable

> **Status:** Review
> **Delivers:** CR0371
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0092
> **Depends on:** US0282
> **Points:** 3

## User Story

**As a** sprint operator
**I want** a re-run close to show whether the outstanding set is shrinking
**So that** a spiral is visible rather than inferred, and hard gates stay hard

## Acceptance Criteria

### AC1: repeated closes report the outstanding-set trend

- **Given** a close attempted more than once
- **When** a close is re-run
- **Then** it reports whether the outstanding set shrank or grew since the previous attempt
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_reclose_reports_outstanding_set_trend
- **Verified:** yes (2026-07-20)

### AC2: a hard correctness gate is never waivable

- **Given** a blocker that is a failing test or a red gate rather than ceremony debt
- **When** the operator chooses file-and-close
- **Then** it is still refused - filing is for administrative blockers, never for correctness
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_hard_correctness_gate_refuses_file_and_close
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
