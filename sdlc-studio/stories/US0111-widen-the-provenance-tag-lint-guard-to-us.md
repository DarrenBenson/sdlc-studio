# US0111: Widen the provenance-tag lint guard to US-form and non-leading ids (CR0201)

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0025
> **Persona:** Engineering seat
> **Affects:** tools/lint-style.sh, tools/tests/test_lint_style.py

## User Story

**As a** maintainer relying on the style gate to keep provenance tags out of shipped files
**I want** the guard to catch US-form ids and ids not immediately after the paren
**So that** a tag like `(US0101/CR0186)` in a shipped comment fails the gate instead of slipping through

Delivers CR0201.

## Acceptance Criteria

### AC1: the guard flags a US-form and a non-leading provenance id in a shipped file

- **Given** a fixture shipped file containing `(US0101/CR0186)` and `(see CR0186)`
- **When** `lint-style.sh` runs over it
- **Then** it fails, naming the offending line
- **Verify:** pytest tools/tests/test_lint_style.py::ProvenanceGuardTests

### AC2: a legitimate non-provenance parenthetical still passes

- **Given** a fixture file with `(for example)` and a code identifier like `(US_DOLLAR)`
- **When** the guard runs
- **Then** it does not flag them (no false positive)
- **Verify:** pytest tools/tests/test_lint_style.py::ProvenanceGuardTests

### AC3: existing shipped files are audited and any leaked tag removed

- **Given** the shipped `scripts/` and `reference-*.md` tree
- **When** the widened guard runs over the repo
- **Then** it passes (any tag the old pattern let through, e.g. `verify_ac.py` `(US0001 ...)`, is removed)
- **Verify:** shell bash tools/lint-style.sh

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0201 (guard blind spot) |
