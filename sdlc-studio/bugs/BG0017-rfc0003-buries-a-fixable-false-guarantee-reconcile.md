# BG-0017: RFC0003 buries a fixable false-guarantee (reconcile 'Idempotent') inside an unsettled RFC, so the wrong doc stays uncorrected

> **Status:** Closed
> **Severity:** Medium
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

RFC0003 bundles a genuine design question (promote reconcile's apply into the script) with a present-tense documentation defect: reference-reconcile.md:270 asserts reconcile is 'Idempotent', which is false because the apply is done by Claude in prose, not deterministically by the read-only script.

## Problem

reference-reconcile.md:270 states 'Idempotent. Running reconcile twice produces the same result', but reconcile.py is read-only (the prose apply is non-deterministic, and LL0001 records 15 stale rows / 82+ unchecked boxes / 14 stale refs that prose passes missed). RFC0003 folds this false-guarantee correction and the apply-promotion into one binary D1 marked Open, so the wrong doc stays uncorrected indefinitely while the design question is debated.

## Proposed Fix

Split RFC0003: file the documentation correction as a Bug/fast CR and reword reference-reconcile.md:270 to scope idempotency to what the script actually guarantees (its read-only detection is deterministic; the prose apply is not). Keep the reconcile --apply promotion as the RFC's actual design decision; the false-guarantee fix must not wait on the unsettled apply question.

## Evidence

reference-reconcile.md:270 'Idempotent. Running reconcile twice produces the same result' vs reconcile.py docstring 'Read-only: emits a JSON report; Claude ... does the editing'

## Impact

A user trusting the documented 'Idempotent' guarantee assumes running reconcile twice is safe and converged, when the prose apply step can miss edits; the wrong doc actively misleads until the whole RFC is resolved.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: design-rfc) |
