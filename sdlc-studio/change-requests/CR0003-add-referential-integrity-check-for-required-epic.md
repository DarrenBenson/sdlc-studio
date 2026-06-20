# CR-0003: Add referential-integrity check for required Epic/Story link fields and dangling ID references

> **Status:** Complete
> **Priority:** High
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** reference-outputs.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Required Epic/Story link fields and the existence of the IDs they reference are never validated deterministically; a story missing its mandatory Epic link, or pointing at a non-existent EP0099, passes validate.py clean.

## Problem

reference-outputs.md:408-413 declares link fields Required (Epic in Story/Plan/Bug/Test-Spec/Workflow; Story in Plan/Bug/Test-Spec/Workflow). Nothing enforces this. validate.py validates a single file's own fields but never reads the '> **Epic:**'/'> **Story:**' lines, never checks they are present where required, and never resolves the referenced ID to a file on disk. reconcile.py reconciles each type's own index in isolation (reconcile.py:26-35) with no cross-type link awareness. This is a purely mechanical graph check (parse link field -> norm_id -> assert a matching artifact file exists), exactly what the doctrine says scripts should own, yet it is left to Claude prose during reviews. sdlc_md already provides extract_field, norm_id, and artifact_files to implement it.

## Proposed Changes

### Item 1: Add referential-integrity check for required Epic/Story link fields and dangling ID references

**Priority:** High **Effort:** TBD

Add a referential-integrity check (to validate.py or a new reconcile scope) that per artifact (a) asserts required link fields are present per the reference-outputs.md:408-413 matrix and (b) resolves each referenced ID via norm_id against the on-disk census, flagging dangling references. Emit JSON findings, non-zero exit on missing-required, advisory on dangling.

## Impact Assessment

### Existing Functionality

Broken or missing traceability links (orphan stories, dependencies on deleted epics) go undetected until a human review notices, defeating the 'full traceability' the hierarchy promises; a deterministic graph check is replaced by manual prose inspection. Quality risk high.

## Acceptance Criteria

- [x] A story missing its required `Epic` link is flagged with a non-zero exit; a well-formed story passes.
- [x] A reference to a non-existent ID (e.g. `EP0099`) is reported as a dangling reference (advisory), resolved via `norm_id` against the on-disk census.
- [x] Findings are emitted as JSON and the check is unit-tested.

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (determinism-sprint) | Complete - delivered as US0012 (scripts/integrity.py), TDD'd, critic-approved |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism; evidence: reference-outputs.md:408-413 (link fields marked Required) vs validate.py:66-112 (no Epic/Story-link rule) and reconcile.py:26-35 (per-type isolation, no cross-reference resolution)) |
