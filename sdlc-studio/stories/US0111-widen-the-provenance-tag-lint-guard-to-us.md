# US0111: Widen the provenance-tag lint guard to US-form and non-leading ids (CR0201)

> **Status:** Done
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

### AC1: the guard flags a US-led provenance pair and a CR/BG/RFC-led tag

- **Given** a fixture shipped file containing `(US0101/CR0186)` (the form the old pattern missed) and `(CR0186)`
- **When** `lint-style.sh` runs over it
- **Then** it fails, naming the offending line
- **Verify:** pytest tools/tests/test_lint_style.py::ProvenanceGuardTests
- **Verified:** yes (2026-07-09)

### AC2: legitimate example ids still pass (no false positive)

- **Given** a fixture file with example ids - a comma list `(US0045, US0046)`, a range `(US0023-US0064)`, a lone `(US0001)`, and an id trailing narrative text `(e.g. CR0003)` - which are indistinguishable from a citation and legitimate in tree diagrams / sample output
- **When** the guard runs
- **Then** it does not flag them
- **Verify:** pytest tools/tests/test_lint_style.py::ProvenanceGuardTests
- **Verified:** yes (2026-07-09)

### AC3: existing shipped files are audited and leaked US-pair tags removed

- **Given** the shipped `scripts/`, `reference-*.md`, `help/` and `templates/config*.yaml` tree (the guard glob now also covers the consuming-facing config templates)
- **When** the widened guard runs over the repo
- **Then** it passes (the US-pair tags the old pattern let through - e.g. `(US0092/CR0195)`, `(US0090/CR0194)` in scripts, reference docs, and `config-defaults.yaml` - are removed)
- **Verify:** shell bash tools/lint-style.sh
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0201 (guard blind spot) |
