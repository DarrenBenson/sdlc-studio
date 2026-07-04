# BG-0002: reconcile.py and status.py both omit bug and workflow artifact types from their deterministic census

> **Status:** Closed
> **Severity:** High
> **Reporter:** Adversarial Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

Two first-class artifact types (bug, workflow) are invisible to both deterministic surfaces: status pillars never count them and reconcile never builds their index census, despite a shipped bug index template and docs promising reconcile covers every indexed type.

## Problem

status.py gather() calls count_by_status only for epic, story, and test-spec (status.py:55-57), so bug (BG) and workflow (WF) - both in ARTIFACT_TYPES with their own STATUS_VOCAB and full status flows (reference-outputs.md:120 bug, :189 workflow) - contribute nothing to the four-pillar census. reconcile.py's _DEFAULT_TYPES (line 35) = story/epic/cr/rfc/plan/test-spec and SCOPE_TYPES has no bugs/workflows scope, so bug/workflow index drift (stale statuses, missing/orphan rows, wrong summary counts) is never detected. This directly contradicts reference-reconcile.md:66 ('applies to EVERY indexed type: stories, epics, plans, test-specs, bugs, CRs, RFCs') and a shipped templates/indexes/bug.md with a full summary table. All bug/workflow tallies fall back to Claude scanning directories in prose, the exact hand-work both scripts exist to eliminate.

## Proposed Fix

Add bug and workflow counts to status.py (a Bugs line: open/in-progress/fixed; a Workflows line). Add 'bugs': ['bug'] and 'workflows': ['workflow'] to reconcile.py SCOPE_TYPES and include 'bug' (and 'workflow' if it carries an index) in `_DEFAULT_TYPES` so index drift is detected for every indexed type the docs promise. Confirm bugs/_index.md follows the | Status | Count | summary convention parse_index expects.

## Evidence

.claude/skills/sdlc-studio/scripts/reconcile.py:35 (_DEFAULT_TYPES excludes bug and workflow) and reference-reconcile.md:66 ('applies to EVERY indexed type: ... bugs ...')

## Impact

Open bugs and stalled workflows never surface in the deterministic dashboard or drift detector, contradicting both scripts' stated guarantee. Health of two artifact types depends on non-deterministic, token-heavy manual scanning. Quality risk high.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism) |
