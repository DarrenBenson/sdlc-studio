# US0260: Drift guard: schema doc vocabularies must match the enforcing code

> **Status:** Ready
> **Delivers:** RFC0047
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_schema_contract.py
> **Epic:** EP0084
> **Points:** 3

## User Story

**As a** maintainer changing templates, vocabularies or the validator
**I want** a test that fails when reference-schema.md diverges from what the code enforces
**So that** the published contract cannot rot silently - the cheap version of RFC0047 option C's promise, keeping option B honest

## Context

The guard parses the contract document's declared vocabularies and compares them against the code's canonical constants (`lib/sdlc_md.py` / `validate.py` are the source of truth - the doc must match the code, never the reverse). Minimum contract surfaces to guard: the status vocabulary (per-type where the code distinguishes it) and the schema version stamp (masthead vs `config-defaults.yaml`, extending US0259's ship-time check into a standing gate). The test lives in `scripts/tests/`, so both `unittest discover` gates (npm test, the pre-commit hook, `gate.py`) pick it up with no wiring. A parser that silently extracts nothing must fail, not pass - an emptied or renamed table is exactly the drift being guarded against.

## Acceptance Criteria

### AC1: Status vocabulary in the doc matches the code

- **Given** the status vocabulary table(s) in `reference-schema.md` and the canonical vocabulary constants in the skill's code
- **When** the guard test runs
- **Then** every status the code enforces appears in the doc and the doc lists no status the code does not know - set equality, with a diff in the failure message naming what drifted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_schema_contract.py::StatusVocabularyContractTests

### AC2: Version stamp agreement is a standing gate

- **Given** the masthead version in `reference-schema.md` and the `schema_version` default in `templates/config-defaults.yaml`
- **When** the guard test runs
- **Then** the two values are equal, so a version bump that touches only one surface fails the suite
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_schema_contract.py::VersionStampContractTests

### AC3: The guard cannot pass vacuously

- **Given** a contract document whose vocabulary table has been emptied, renamed, or restructured so the parser finds nothing
- **When** the guard test runs
- **Then** it fails with a message saying the contract surface could not be located - extraction is asserted non-empty before any comparison
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_schema_contract.py::ParserHonestyTests

### AC4: The guard runs in the standard suite with the rest of the skill tests

- **Given** the shipped test file in `scripts/tests/`
- **When** the standard discovery gate runs
- **Then** the guard is collected and passes as part of the ordinary suite
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p "test_schema_contract.py"

### AC5: The change is recorded in the changelog

- **Given** the commit that ships the guard
- **When** CHANGELOG.md is read
- **Then** the [Unreleased] section records the schema-contract drift guard
- **Verify:** grep "test_schema_contract" CHANGELOG.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-17 | sdlc-studio | ACs groomed: 5 executable ACs; named test classes per AC; vacuous-pass honesty AC |
