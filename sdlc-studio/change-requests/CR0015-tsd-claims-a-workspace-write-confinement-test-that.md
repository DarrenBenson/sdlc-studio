# CR-0015: TSD claims a workspace write-confinement test that does not exist

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** tsd.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The TSD asserts in three places that read-only/write-confinement (contract rule 5) is covered by tests, but no test snapshots the fixture workspace and verifies nothing outside .local/ or the named target changed.

## Problem

tsd.md:38-39, :119 ('Confirms read-only confinement'), :195 ('writes confined to .local/ or named files') claim confinement coverage. The suite has no before/after workspace snapshot assertion; the only adjacent checks are plan.py's no-overwrite and reconcile's no-overwrite-Done, neither of which is a confinement check. The headline contract-rule-5 guarantee the TSD says is covered is not exercised.

## Proposed Changes

### Item 1: TSD claims a workspace write-confinement test that does not exist

**Priority:** Medium **Effort:** TBD

Add a fixture test per side-effecting script that snapshots the workspace tree (paths + hashes), runs the script, and asserts only .local/ and the named target changed. Until that exists, downgrade the TSD wording from 'Confirms read-only confinement' to 'confinement is a contract requirement, not yet asserted by a test'.

## Impact Assessment

### Existing Functionality

Contract rule 5 is the central safety property of the read-only helpers and the basis of the Performance/Security framing; the TSD claims a test proves it but none does, so a regression writing stray files would pass the gate undetected.

## Acceptance Criteria

- [ ] Add a fixture test per side-effecting script that snapshots the workspace tree (paths + hashes), runs the script, and asserts only .local/ a

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: tsd) |
