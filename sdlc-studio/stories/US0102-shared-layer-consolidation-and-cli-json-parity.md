# US0102: Shared-layer consolidation and CLI JSON parity

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0022
> **Persona:** Engineering seat
> **Affects:** scripts/lib/sdlc_md.py, scripts/reconcile.py, scripts/tests/test_reconcile.py, scripts/tests/test_sdlc_md.py

## User Story

**As a** maintainer of the skill's scripts
**I want** the duplicated `find_by_id`/`linked_to_epic` on the shared layer, `reconcile.py`'s docstring accurate, and `apply`/`revision`/`rebuild` to speak `--format json`
**So that** a lookup fix lands in one place and every subcommand is scriptable

Delivers CR0187 items 1-3 (maintainability, no behaviour change).

## Acceptance Criteria

### AC1: find_by_id / linked_to_epic live on the shared layer

- **Given** the duplicate copies of `find_by_id` / `linked_to_epic`
- **When** the code is inspected
- **Then** the canonical implementation lives in `lib/sdlc_md.py` and the former duplicates delegate to it (one source of truth)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::FindByIdTests

### AC2: reconcile.py's docstring is accurate

- **Given** `reconcile.py`
- **When** its module docstring is read
- **Then** it lists all four subcommands (detect/apply/archive/rebuild) and scopes read-only to `detect`
- **Verify:** shell python3 -c "import ast,pathlib; d=ast.get_docstring(ast.parse(pathlib.Path('.claude/skills/sdlc-studio/scripts/reconcile.py').read_text())); print('OK') if all(s in d for s in ('detect','apply','archive','rebuild')) else exit(1)"

### AC3: apply / revision / rebuild accept --format json

- **Given** `reconcile apply`, `revision`, and `rebuild`
- **When** invoked with `--format json`
- **Then** each prints its existing result structure as JSON (parity with `detect`)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::FormatJsonParityTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0187 (shared-layer + CLI parity) |
