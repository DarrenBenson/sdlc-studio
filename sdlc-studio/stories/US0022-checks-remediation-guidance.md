# US0022: deterministic checks emit remediation guidance

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0025, remediation)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator on a fresh project
**I want** each check to tell me how to fix what it found and whether it's real
**So that** a wall of findings (e.g. consuming repo A's "575 not conformant") comes with
instructions, not just counts (CR0025).

## Context

Implements CR0025. A shared `REMEDIATION` registry in `lib/sdlc_md.py` maps each
check's finding-kind to a one-line fix hint; `remediation_lines(check, kinds)`
returns the hints for the kinds present. conformance / integrity / audit / reconcile
print a `Guidance:` block in text mode (JSON unchanged); conformance adds a
bulk-pattern note distinguishing an unadopted discipline from per-unit drift.

## Acceptance Criteria

### AC1: Shared registry returns hints in stable order

- **Given** finding-kinds present for a check
- **When** `remediation_lines(check, kinds)` runs
- **Then** it returns the registered hint per present kind in registry order, and nothing for absent kinds or an unknown check
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::RemediationTests
- **Verified:** yes (2026-06-20)

### AC2: Every check prints Guidance in text mode

- **Given** a workspace with findings
- **When** each check runs in text mode
- **Then** conformance/integrity/audit/reconcile print a `Guidance:` block with fix hints for the findings present
- **Verified:** yes (2026-06-20)

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::GuidanceTests

### AC4: integrity prints Guidance in text mode

- **Given** a integrity finding
- **When** it is rendered in text mode
- **Then** it carries its Guidance line, checked per checker rather than by one
  selector standing for four - all four sat stacked in AC2 and never ran (BG0265)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_integrity.py::GuidanceTests
- **Verified:** yes (2026-07-22)

### AC5: audit prints Guidance in text mode

- **Given** a audit finding
- **When** it is rendered in text mode
- **Then** it carries its Guidance line, checked per checker rather than by one
  selector standing for four - all four sat stacked in AC2 and never ran (BG0265)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit.py::GuidanceTests
- **Verified:** yes (2026-07-22)

### AC6: reconcile prints Guidance in text mode

- **Given** a reconcile finding
- **When** it is rendered in text mode
- **Then** it carries its Guidance line, checked per checker rather than by one
  selector standing for four - all four sat stacked in AC2 and never ran (BG0265)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::GuidanceTests
- **Verified:** yes (2026-07-22)

### AC3: conformance interprets bulk patterns

- **Given** most units missing the same stage
- **When** conformance runs
- **Then** it notes "likely an unadopted discipline ... not per-unit drift"
- **Verify:** grep "unadopted" .claude/skills/sdlc-studio/scripts/conformance.py
- **Verified:** yes (2026-07-10)

## Implementation

`lib/sdlc_md.py`: `REMEDIATION` + `remediation_lines`. Guidance block in each
check's `cmd_*` text branch; conformance bulk-pattern note.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0025) | Decomposed from CR0025 (remediation) |
