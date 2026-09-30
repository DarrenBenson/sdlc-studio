# BG0858: migrate names nothing when the conformance lane fails only on ULID-id units or repo-wide failures, so a schema v3 project meets the failure at the gate unannounced

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, changelog.d/BG0858.md
> **Evidence:** BG0854 build report (subagent aebb1ffe), 2026-09-30; migrate.py _conformance_cutoff
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T11:16:09Z

## Summary

Found building BG0854 (RUN-01M3RPSK, 2026-09-30): `_conformance_cutoff` in migrate.py returns no item when there are no numbered failing units, so when the gate's conformance lane fails only on v3 ULID-id units or only on repo-wide failures, migrate names nothing while the gate fails. BG0854's end-to-end test agrees on all four lanes for a v4.1-shaped fixture with numbered ids; a v3 project is outside it. The goal of RUN-01M3RPSK (migrate predicts the gate's conformance failures) holds for numbered-id projects only.

## Steps to Reproduce

On a fixture whose only non-conformant units carry v3 ULID ids (or whose only conformance failure is repo-wide), run migrate.py --format json and gate.py --format json: the gate's conformance lane fails, migrate has no conformance item.

## Proposed Fix

When the lane fails but no numbered unit is found, still emit the conformance item with lane, count (as the gate computes it) and the per-unit or repo-wide remedies, with line None, as BG0843 already does for the engagement floor's ULID units.

## Acceptance Criteria

- [ ] **AC1** Given a committed fixture whose conformance lane fails only on a v3 ULID-id unit, when migrate.py --format json runs, then a conformance item carries lane conformance and the gate's count, with line None. Fails on: HEAD, which emits no item
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py::MigrateCutoffTests::test_a_ulid_only_conformance_failure_is_still_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
