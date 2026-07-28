# US0532: The corpus read is measured by a test that fails if it grows back to per-unit, so the fix cannot silently regress

> **Status:** Ready
> **Delivers:** CR0465
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0181
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an engineer maintaining reconcile
**I want** the corpus read count pinned by a test that fails if it scales with the unit count
**So that** the fix cannot silently regress into per-unit reading as the workspace grows

## Acceptance Criteria

### AC1: the read count is pinned, so a regression to per-unit reddens

- **Given** a workspace whose unit count is doubled
- **When** the sweep detectors run over both
- **Then** the number of corpus reads is unchanged between the two, so a return to per-unit reading fails the test rather than only slowing the gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::CorpusReadOnceTests::test_the_read_count_does_not_scale_with_unit_count

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
