# US0133: refine add safety: require an already-decomposed request, de-duped append, atomic with rollback, reconcile-clean

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0036
> **Points:** 2

## User Story

**As an** operator using refine add
**I want** it to require an already-decomposed request, de-dupe the append, and be atomic
**So that** add can never clobber an earlier slice, duplicate a child, or leave a half-state.

## Acceptance Criteria

### AC1: add requires an already-decomposed request

- **Given** a request with no `Decomposed-into` (never refined)
- **When** `refine add` runs
- **Then** it refuses, pointing at `refine apply` for the first epic
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests::test_refine_add_refuses_an_undecomposed_request
- **Verified:** yes (2026-07-15)

### AC2: the append de-dupes and is atomic

- **Given** a repeated epic id in the append, or a bad story title on the add path
- **When** `refine add` (or `_write_decomposed`) runs
- **Then** the `Decomposed-into` list de-dupes by normalised id, and a bad title mints nothing (the first slice's epic/stories survive untouched)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests::test_refine_add_dedupes_and_is_atomic
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
