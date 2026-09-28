# BG0842: migrate reports 2 index drift items on a v4.1 project whose gate reconcile lane fails on 28, because project upgrade counts two of reconcile's nine drift sources

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, changelog.d/BG0842.md
> **Evidence:** docs/upgrade-rehearsal-v6.md (US0962), v4.1 row; project_upgrade.py plan(): drift = `sum(len(reconcile.detect_type(t, root)['drift']) ...)`; `gate.py` `_reconcile()`: `reconcile.detect_all`
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T19:42:37Z

## Summary

US0962 rehearsal (a v4.1 project of 687 stories, skill 6.0.0-rc.1 at 5e45cbf9): `migrate` and `migrate --apply` both report '2 index/status drift item(s) - review with `/sdlc-studio reconcile`' as a needs-a-human item, while `gate.py` on the same tree, before and after the apply, fails its reconcile lane with '28 drift item(s) (+1 awaiting another gate, not blocking)'. `project_upgrade.plan` sums `reconcile.detect_type(t)` per artefact type; the gate's `_reconcile` lane reads `reconcile.detect_all`, the one sweep of all nine drift sources, and its own comment records that an enumerated list 'silently exempts what it forgot'. The upgrader is told of 2 items and meets 28 at the gate.

## Steps to Reproduce

On a scratch copy of a project with epic-breakdown or link-asymmetry drift but clean per-type index rows, run `migrate.py --root <copy>` and `gate.py --root <copy>`: migrate names fewer drift items than the gate's reconcile lane counts.

## Proposed Fix

Count drift in project upgrade from `reconcile.detect_all`, less what the gate itself does not block on (the `blocked_by` items and what `reconcile.settled_items` would settle), through one shared helper the gate lane also calls, so the report and the lane cannot disagree.

## Acceptance Criteria

- [ ] **AC1** Given a fixture workspace whose drift includes a kind `reconcile.detect_type` does not return (e.g. an epic-breakdown or link-asymmetry item), when `migrate.py --format json` runs, then its index-drift needs-a-human item carries the same count the gate's reconcile lane reports on that tree. Fails on: the per-type sum, which omits the extra kind
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::UpgradeDriftCountTests::test_the_drift_count_is_the_gates_reconcile_count
- [ ] **AC2** Given a fixture with no drift, then migrate names no index-drift item. Fails on: a count that includes blocked or settle-only items the gate does not block on
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::UpgradeDriftCountTests::test_no_drift_names_no_item

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
