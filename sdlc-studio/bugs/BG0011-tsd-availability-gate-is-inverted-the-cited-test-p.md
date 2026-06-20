# BG-0011: TSD Availability gate is inverted: the cited test proves a hard abort (exit 127), not graceful degradation

> **Status:** Open
> **Severity:** Medium
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The TSD maps the 'sync degrades gracefully' NFR to a passing unit gate, but the cited tests assert github_sync hard-fails with exit 127 when gh is absent.

## Problem

tsd.md:236 claims 'github_sync.py graceful-degradation paths are unit-tested with gh absent/mocked (Yes (unit))', mapping the PRD Availability NFR (prd.md:249-250 'degrade gracefully'). But github_sync.gh() raises RuntimeError and main() returns 127 when gh is missing (github_sync.py:70-71, :576-578), and test_github_sync.py asserts rc == 127. The TSD launders a spec-vs-code contradiction into a satisfied gate.

## Proposed Fix

Reword the Availability gate row to state the tested behaviour: github_sync aborts with a clear error (exit 127) when gh is absent, and offline capability comes from the core pipeline scripts that make no network calls. Either downgrade the 'graceful-degradation' wording or raise a CR against github_sync.py and mark the NFR not-yet-satisfied.

## Evidence

tsd.md:236 'graceful-degradation paths are unit-tested ... Yes (unit)' vs test_github_sync.py asserting rc == 127 and github_sync.py:576-578 (except RuntimeError -> return 127)

## Impact

A reader trusts that sync degrades gracefully offline because the TSD says a unit gate proves it; in fact sync hard-fails with 127, which can break automation that assumes a soft no-op. The NFR-to-evidence traceability is inverted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: tsd) |
