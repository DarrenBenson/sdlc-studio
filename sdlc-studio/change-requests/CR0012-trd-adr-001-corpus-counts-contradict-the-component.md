# CR-0012: TRD ADR-001 corpus counts contradict the Component Overview table and reality

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** trd.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

ADR-001's Context cites ~63 templates and ~15-19 best-practices to justify the router pattern, but the section-3 table and the live tree say 72 templates and 19 best-practices.

## Problem

trd.md:434-435 sizes the corpus as '~30 help files, ~63 templates, ~15-19 best-practice guides', while trd.md:109-112 gives 31 help, 72 templates, 19 best-practices, matching the live tree (find templates -type f = 72; ls best-practices/*.md = 19). The ~63 figure is off by ~13% and the loose ranges disagree with the document's own precise figures. These are the numbers ADR-001 uses to justify progressive disclosure.

## Proposed Changes

### Item 1: TRD ADR-001 corpus counts contradict the Component Overview table and reality

**Priority:** Low **Effort:** TBD

Reconcile ADR-001's Context figures to the section-3 table (42 reference, 31 help, 72 templates, 19 best-practices) and drop the approximate ranges, or replace the hard numbers with a 'see the component table' reference so the two cannot drift.

## Impact Assessment

### Existing Functionality

An internal numeric contradiction in a load-bearing ADR of a document whose stated purpose is a precise rebuild blueprint erodes confidence in the other corpus counts the scaling argument leans on.

## Acceptance Criteria

- [ ] Reconcile ADR-001's Context figures to the section-3 table (42 reference, 31 help, 72 templates, 19 best-practices) and drop the approximate

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: trd) |
