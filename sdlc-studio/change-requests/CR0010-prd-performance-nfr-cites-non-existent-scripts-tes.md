# CR-0010: PRD Performance NFR cites non-existent 'scripts/tests timings' evidence

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** prd.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The Performance NFR points at a timing/perf test that does not exist in scripts/tests.

## Problem

prd.md:233-234 claims reconcile/status 'run in well under a second on a typical project (see scripts/tests timings)'. There is no timing/perf/benchmark assertion in scripts/tests; the suite reports total runtime but no per-command 'under a second' test. The claim presents itself as code-backed in a [HIGH] extraction but points at a non-existent oracle.

## Proposed Changes

### Item 1: PRD Performance NFR cites non-existent 'scripts/tests timings' evidence

**Priority:** Low **Effort:** TBD

Drop the parenthetical false citation and soften to an observed/qualitative statement, or add an actual timing assertion in scripts/tests and cite it. Do not reference 'scripts/tests timings' until such a test exists.

## Impact Assessment

### Existing Functionality

A reviewer validating the spec against tests (the doctrine's own oracle) finds the cited evidence absent, eroding trust in other [HIGH]-confidence claims.

## Acceptance Criteria

- [ ] Drop the parenthetical false citation and soften to an observed/qualitative statement, or add an actual timing assertion in scripts/tests an

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: prd) |
