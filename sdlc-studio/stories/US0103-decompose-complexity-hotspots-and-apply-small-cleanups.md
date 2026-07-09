# US0103: Decompose complexity hotspots and apply small cleanups

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0022
> **Persona:** Engineering seat
> **Affects:** scripts/reconcile.py, scripts/tests/test_table_parsers.py, scripts/tests/test_verify_ac.py

## User Story

**As a** maintainer
**I want** the four named complexity hotspots decomposed into helpers, the flagged test issues fixed, and the six small cleanups (log roll, one-line debug on swallowed advisories) applied
**So that** the debt that lets Medium-severity defects recur is paid down without changing behaviour

Delivers CR0187 items 4-6. Depends on US0102 (same shared-layer / reconcile surface).

> **Depends on:** US0102

## Acceptance Criteria

### AC1: The four named hotspots are decomposed with no behaviour change

- **Given** the four complexity hotspots named in RV0006
- **When** they are refactored into smaller helpers
- **Then** each hotspot's cognitive complexity drops and the existing tests pass unchanged (behaviour-preserving)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_reconcile.py 2>&1 | grep -qE "^OK"
- **Verified:** yes (2026-07-09)

### AC2: The flagged test issues are fixed

- **Given** `test_table_parsers.py:85` and the verify tests
- **When** they run
- **Then** the regex uses a raw string and the verify tests no longer leak stdout
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_table_parsers.py
- **Verified:** yes (2026-07-09)

### AC3: The six small cleanups are applied

- **Given** the six named small cleanups
- **When** applied
- **Then** `.local` logs roll (bounded size) and `SDLC_DEBUG=1` emits one line from each named swallowed-advisory site
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DebugTraceTests
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0187 (hotspots + cleanups) |
