# US0112: Hygiene: close fixed bugs, archive over-threshold indexes, accept v3 ULID ids in validate

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0025
> **Persona:** Engineering seat
> **Affects:** sdlc-studio/bugs, scripts/validate.py, scripts/tests/test_validate.py, sdlc-studio/stories/archive, sdlc-studio/change-requests/archive

## User Story

**As a** maintainer clearing the decks for v4
**I want** the three fixed-but-unclosed bugs closed, the over-threshold indexes archived, and `validate` to accept a v3 ULID id
**So that** the open-bug count reaches 0 (an rc-tag gate), the live indexes stay bounded, and validate does not reject a v4 project's ULID-form ids

Clears the residual bug backlog + the standing archival advisory + a v4-readiness validate gap.

## Acceptance Criteria

### AC1: the three fixed bugs are closed, backed by their regression tests

- **Given** BG0067, BG0068, BG0069, BG0070 (all `Fixed`, each with a passing regression test)
- **When** their regression tests are re-run and each is transitioned
- **Then** each reaches a terminal status and the open-bug count is 0
- **Verify:** shell test "$(grep -l '> \*\*Status:\*\* Closed' sdlc-studio/bugs/BG0067*.md sdlc-studio/bugs/BG0068*.md sdlc-studio/bugs/BG0069*.md sdlc-studio/bugs/BG0070*.md | wc -l)" -eq 4
- **Verified:** yes (2026-07-10)

### AC2: the over-threshold story and cr indexes are archived, census unaffected

- **Given** the live story index (over the `indexes.archive_after` threshold) and cr index
- **When** `archive.py` archives their terminal rows to a release sub-index
- **Then** the live indexes drop under the threshold, the reconcile archival advisory clears, and the census (drift 0) is unaffected
- **Verify:** shell test -z "$(python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect 2>&1 | grep -E 'advisory \((story|cr)\).*terminal row')" && python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect
- **Verified:** yes (2026-07-10)

### AC3: validate accepts a v3 ULID id (no id-format false error)

- **Given** a v3 artifact whose id is a ULID (not a v2 sequential id)
- **When** `validate` checks it
- **Then** it does not raise an `id-format` error for the ULID form
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::UlidIdFormatTests
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed: bug-close + archival + v3 ULID validate (spec-guard basename note left deferred) |
