# BG-0016: EP0004's PRD Reference points to section 10 with a non-existent 'Validation Requirement' link text

> **Status:** Open
> **Severity:** Low
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

Every other epic links its PRD Reference to the Feature Inventory that maps its features; EP0004 alone links to §10 Quality Assessment under the made-up heading 'Validation Requirement'.

## Problem

EP0004-testing.md:16 reads '**PRD Reference:** [Validation Requirement](../prd.md#10-quality-assessment)'. EP0004's three features (Test spec/automation/environment) are mapped in the Feature Inventory rows (prd.md:144-146, §3), not in §10, and there is no 'Validation Requirement' heading anywhere. The upward link is misdirected and the link text names a non-existent artefact.

## Proposed Fix

Change EP0004's PRD Reference to '[Feature Inventory](../prd.md#3-feature-inventory)' to match every other epic and point at the rows that map its features. If a §10 link is also wanted, add it as a secondary reference with accurate text.

## Evidence

EP0004-testing.md:16 '[Validation Requirement](../prd.md#10-quality-assessment)' vs EP0004 feature rows at prd.md:144-146 under §3 (no 'Validation Requirement' heading)

## Impact

Following EP0004's traceability link upward lands on the Quality Assessment narrative, not the feature-to-epic mapping, breaking the epic->feature trace; the fabricated link text suggests a heading that does not exist.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: traceability) |
