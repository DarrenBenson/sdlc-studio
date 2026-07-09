# US0102: Shared-layer consolidation and CLI JSON parity

> **Status:** Done
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

### AC1: find_by_id / story_epic live on the shared layer

- **Given** the duplicate copies of "find an artifact by id" (`audit.find_artifact`,
  `transition._find`) and "a story's epic" (`lite_profile._story_epic`)
- **When** the code is inspected
- **Then** canonical `find_by_id` / `story_epic` live in `lib/sdlc_md.py` (with alias resolution)
  and the former duplicates delegate to them (one source of truth)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::FindByIdTests
- **Verified:** yes (2026-07-09)

### AC2: reconcile.py's docstring lists its subcommands and scopes read-only to detect

- **Given** `reconcile.py`
- **When** its module docstring is read
- **Then** it lists every subcommand (detect/apply/fields/archive) and marks `detect` READ-ONLY
- **Verify:** shell python3 -c "import ast,pathlib; d=ast.get_docstring(ast.parse(pathlib.Path('.claude/skills/sdlc-studio/scripts/reconcile.py').read_text())); print('OK') if all(s in d for s in ('detect','apply','fields','archive')) and 'READ-ONLY' in d else exit(1)"
- **Verified:** yes (2026-07-09)

### AC3: every reconcile subcommand accepts --format json (parity)

- **Given** `reconcile detect/apply/fields/archive`
- **When** each is invoked with `--format json`
- **Then** each prints its result structure as JSON (the parity is locked by a test so a new
  subcommand cannot ship without it)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::FormatJsonParityTests
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0187 (shared-layer + CLI parity) |
