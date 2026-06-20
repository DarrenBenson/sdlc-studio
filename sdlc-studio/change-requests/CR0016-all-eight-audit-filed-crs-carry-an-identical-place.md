# CR-0016: All eight audit-filed CRs carry an identical placeholder AC that asserts nothing about the change

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** CR0002-add-deterministic-duplicate-id-collision-detector.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

CR0002-CR0009 each have exactly one acceptance criterion - 'Change implemented and verified; lint and tests green' - a tautology identical across eight different changes, not machine-checkable against any of them.

## Problem

CR0002-CR0009 line 36 are all '[ ] Change implemented and verified; lint and tests green.' This says 'done when done' and is meaningless for CRs that by their own admission add the behaviours that are the untested gap. RFC0002:118's Epics/Stories lens hunts 'AC not machine-checkable', and the audit prides itself on determinism, yet its own CR ACs cannot fail for the right reason - any reviewer can close them by running the existing suite green. Contrast CR0001 (five specific ACs).

## Proposed Changes

### Item 1: All eight audit-filed CRs carry an identical placeholder AC that asserts nothing about the change

**Priority:** Medium **Effort:** TBD

Replace each placeholder with the concrete, checkable assertion already implied by that CR's Proposed Changes (e.g. CR0002: 'next_id.py --collisions exits non-zero and lists both file paths when two files share a norm_id; validate.py check fails on duplicate IDs'; CR0004: 'review_prep last_modified derives from git log -1 --format=%cI; a malformed last_reviewed yields needs_review plus a warning'). The audit's own determinism standard should apply to the ACs it writes.

## Impact Assessment

### Existing Functionality

Every CR is closeable by a reviewer who runs the existing suite green without implementing the specific guard the CR demands; the findings record a problem but provide no acceptance signal that the fix addresses it, defeating the traceable-AC purpose the skill markets.

## Acceptance Criteria

- [ ] Replace each placeholder with the concrete, checkable assertion already implied by that CR's Proposed Changes (e.g. CR0002: 'next_id.py --co

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: design-rfc) |
