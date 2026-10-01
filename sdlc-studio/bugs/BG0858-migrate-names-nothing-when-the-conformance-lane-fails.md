# BG0858: migrate names nothing when the conformance lane fails only on ULID-id units or repo-wide failures, so a schema v3 project meets the failure at the gate unannounced

> **Status:** Open
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: a ULID fixture with one Done story `US-01M3VEK2` reads `[FAIL] conformance: 1 non-conformant unit(s)` from `gate.py --only conformance`, while `migrate.py --format json` emits only `team-offer`, `index-drift`, `validate-errors` (`_conformance_cutoff` drops every unit whose `id_number` is None). Distinct from US0974, which makes conformance ACCEPT a ULID cutoff; this makes migrate PROPOSE one, so it is blocked by US0974 AC1
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, changelog.d/BG0858.md
> **Evidence:** BG0854 build report (subagent aebb1ffe), 2026-09-30; migrate.py _conformance_cutoff
> **Depends on:** US0974
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T11:16:09Z

## Summary

Found building BG0854 (RUN-01M3RPSK, 2026-09-30): `_conformance_cutoff` in migrate.py returns no item when there are no numbered failing units, so when the gate's conformance lane fails only on v3 ULID-id units or only on repo-wide failures, migrate names nothing while the gate fails. BG0854's end-to-end test agrees on all four lanes for a v4.1-shaped fixture with numbered ids; a v3 project is outside it. The goal of RUN-01M3RPSK (migrate predicts the gate's conformance failures) holds for numbered-id projects only.

## Steps to Reproduce

On a fixture whose only non-conformant units carry v3 ULID ids (or whose only conformance failure is repo-wide), run migrate.py --format json and gate.py --format json: the gate's conformance lane fails, migrate has no conformance item.

## Proposed Fix

Once US0974 makes `conformance.adopt_after` accept a ULID id, `_conformance_cutoff` stops filtering on `id_number` and names the highest failing id by the order the lane compares (number or ULID). When the lane fails on repo-wide failures alone, it still emits its existing `conformance-cutoff` item with the lane's count and no cutoff line. No new item kind or section.

## Acceptance Criteria

- [ ] **AC1** Given a schema v3 fixture whose only non-conformant unit is a Done story with a ULID id, when `migrate.py --format json --root <fixture>` runs, then it emits a `conformance-cutoff` item proposing `conformance.adopt_after: <that ULID id>` with the gate lane's count, and after writing that line `gate.py --only conformance` passes. Fails on: HEAD, which emits no conformance item
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py::MigrateCutoffTests::test_a_ulid_only_conformance_failure_is_still_named
- [ ] **AC2** Given a fixture whose conformance lane fails only on a repo-wide failure, when `migrate.py --format json` runs, then a `conformance-cutoff` item carries the lane's count and no `adopt_after` line. Fails on: HEAD's `if not failing: return []`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py::MigrateCutoffTests::test_a_repo_wide_only_failure_is_still_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
