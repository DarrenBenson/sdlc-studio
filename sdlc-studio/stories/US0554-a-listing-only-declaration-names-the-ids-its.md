# US0554: A listing-only declaration names the ids its structural read depends on, so filing an artefact stops triggering the full suites

> **Status:** Done
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0189
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an agent filing a bug or a change request
**I want** a listing-only declaration to name the artefact ids its structural read actually depends on
**So that** filing an artefact the declaring test never reads stops making the whole tree structural and paying the full suites

## Acceptance Criteria

### AC1: a declaration may name ids as well as a directory

- **Given** a test module declaring `GATE_LISTING_ONLY` with a directory and a set of ids
- **When** the gate reads that declaration
- **Then** both the directory and the id set are parsed, and a malformed id set is refused rather than partially honoured
- **Verify:** manual - retired by US0880: the measured test-relevant set and its listing-only narrowing are deleted, and per-commit selection reads imports, loads and test names only
- **Verified:** manual (2026-09-24) - retired, superseded by US0880

### AC2: a new file under the directory whose id is not named is not structural

- **Given** a declaration naming ids
- **When** an artefact is added under that directory whose id the declaration does not name
- **Then** the file does not enter the test-relevant surface, and the declaring module is not selected for it
- **Verify:** manual - retired by US0880: the measured test-relevant set and its listing-only narrowing are deleted, and per-commit selection reads imports, loads and test names only
- **Verified:** manual (2026-09-24) - retired, superseded by US0880

### AC3: a change to a named id remains structural

- **Given** the same declaration
- **When** an artefact whose id IS named changes or is added
- **Then** the file is structural exactly as before and the declaring module is selected for it
- **Verify:** manual - retired by US0880: the measured test-relevant set and its listing-only narrowing are deleted, and per-commit selection reads imports, loads and test names only
- **Verified:** manual (2026-09-24) - retired, superseded by US0880

### AC4: the fail-safe direction is preserved

- **Given** a declaration that names NO ids, the form every existing module uses
- **When** the gate reads it
- **Then** the whole directory stays structural exactly as now, so the narrowing is opt-in and a module that omits its ids is slower rather than wrong
- **Preserves:** every existing `GATE_LISTING_ONLY` declaration that names no ids keeps its current whole-directory meaning, so this story owns the gate.py seam it shares with US0553
- **Verify:** manual - retired by US0880: the measured test-relevant set and its listing-only narrowing are deleted, and per-commit selection reads imports, loads and test names only
- **Verified:** manual (2026-09-24) - retired, superseded by US0880

### AC5: the root census declares the ids it reads

- **Given** `test_root_census.py`, which reaches named artefacts through `_artefact_on_disk`
- **When** its declaration is read
- **Then** it names exactly the ids the census file lists, and a census id the declaration omits is reported rather than left silently unprotected
- **Verify:** manual - retired by US0880: the measured test-relevant set and its listing-only narrowing are deleted, and per-commit selection reads imports, loads and test names only
- **Verified:** manual (2026-09-24) - retired, superseded by US0880

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
