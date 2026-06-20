# US0012: Referential-integrity check

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0003, determinism-sprint)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** required link fields and referenced IDs validated deterministically
**So that** a story missing its Epic link, or pointing at a non-existent ID, is
caught instead of passing `validate` clean (CR0003).

## Context

Implements CR0003. New `scripts/integrity.py`: required-link presence per the
`reference-outputs.md` matrix (Epic in Story/Plan/Bug/TestSpec/Workflow; Story in
Plan/Bug/TestSpec/Workflow) and dangling-reference detection via `norm_id` against
the on-disk census. Missing-required on an **active** (non-terminal) artifact is an
error (non-zero exit); on a terminal artifact it is advisory (historical); dangling
is advisory. Reuses `lib/sdlc_md`. Pure stdlib.

## Acceptance Criteria

### AC1: Missing required link errors on active artifacts

- **Given** a Ready story with no `Epic` field
- **When** `detect_integrity(root)` runs
- **Then** a `missing-required` finding (severity error) is produced and the CLI exits non-zero; a well-formed story produces none
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_integrity.py::MissingTests::test_active_missing_epic_errors
- **Verified:** yes (2026-06-20)

### AC2: Dangling reference is advisory

- **Given** a story whose `Epic` resolves to a non-existent `EP9099`
- **When** the check runs
- **Then** a `dangling` finding (severity advisory) is produced, resolved via `norm_id` against the census, and the CLI exits 0
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_integrity.py::DanglingTests::test_dangling_advisory
- **Verified:** yes (2026-06-20)

### AC3: Terminal artifact missing link is advisory, and JSON is emitted

- **Given** a Done/Fixed artifact missing a required link
- **When** the check runs
- **Then** the finding is severity advisory (not error), the CLI exits 0, and `--format json` prints findings + a summary
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_integrity.py::TerminalTests::test_terminal_missing_is_advisory
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/integrity.py`: `detect_integrity(root)` + `check` subcommand (model:
`conformance.py`). `REQUIRED_LINKS` matrix; census = `norm_id` of every artifact;
severity error only for missing-required on non-terminal artifacts.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0003) | Decomposed from CR0003 (determinism sprint) |
