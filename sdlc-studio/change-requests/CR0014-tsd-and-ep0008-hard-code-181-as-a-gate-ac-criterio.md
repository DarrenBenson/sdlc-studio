# CR-0014: TSD and EP0008 hard-code '181' as a gate/AC criterion, coupling them to a count that changes every release

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** tsd.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The TSD encodes 'All 181 tests pass' / '181/181' as the blocking criterion in five places, and EP0008's epic AC says '181 passing at extraction'; the real CI gate is count-independent (npm test exits 0), so any test added/removed silently contradicts both documents.

## Problem

tsd.md:43/132/230/242/338 all cite 181 as the gate, and EP0008-tooling-scripts.md:45 bakes '181 passing at extraction' into an epic AC. The actual gate is npm test (lint.yml:27-28) which passes when the discovered suite passes regardless of count. The count is correct today but encoding it as the binding criterion means routine test changes make the stated gate/AC factually wrong in six locations.

## Proposed Changes

### Item 1: TSD and EP0008 hard-code '181' as a gate/AC criterion, coupling them to a count that changes every release

**Priority:** Low **Effort:** TBD

Phrase the TSD gate as 'the full unittest suite passes (npm test exits 0)' and EP0008's AC as a durable property ('every script under scripts/ has unit tests and the suite passes'), keeping '181 at extraction, 2026-06-20' as parenthetical provenance rather than the assertion.

## Impact Assessment

### Existing Functionality

As soon as one test is added, the stated gate/AC is false in six places and any check that greps for the count drifts, inviting churn and false drift reports.

## Acceptance Criteria

- [ ] Phrase the TSD gate as 'the full unittest suite passes (npm test exits 0)' and EP0008's AC as a durable property ('every script under script

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: tsd) |
