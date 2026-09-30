# BG0854: Nothing runs migrate and then the gate on one fixture, so migrate's report drifted from the gate's failing lanes on three lanes unseen

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_gate_agree.py, changelog.d/BG0854.md
> **Depends on:** BG0842, BG0843, BG0844, BG0845
> **Evidence:** docs/upgrade-rehearsal-v6.md 'Reading the gate columns'; goal review round 78 QA seat
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T08:07:44Z

## Summary

The v6 upgrade rehearsal (US0962, docs/upgrade-rehearsal-v6.md) found migrate disagreeing with gate.py on three lanes of a v4.1 project: reconcile (2 items against 28, BG0842), the engagement floor (349 units, not named, BG0843) and conformance (a cutoff that exempts post-adoption units, BG0845). Each was found by a human reading two outputs side by side; no test runs `migrate.py --apply` and then `gate.py` on the same tree, and no migrate test imports gate, so the report and the gate can drift apart again with the suite green. The sprint goal review of 2026-09-30 (round 78, QA seat) named this as the goal's untested claim.

## Steps to Reproduce

grep the migrate and `project_upgrade` tests for a gate invocation: none runs gate.py after migrate on the same fixture.

## Proposed Fix

Give every migrate item that corresponds to a gate lane a `lane` field carrying the gate's own lane name (`reconcile`, `conformance`, `validate`, `engagement-floor`), set where the item is built, so no test or reader keeps a hand-written kind-to-lane map (LL0013). Then one end-to-end test on a COMMITTED git fixture shaped like the rehearsal's v4.1 project: run migrate --apply --format json, commit the apply, run gate.py --format json, take the failing blocking lanes from the gate's own output, and assert migrate carries an item for each with the gate's count. The commit matters: on a dirty tree the gate scopes conformance and validate to the diff and they pass, which is how the rehearsal missed them. It lands after BG0842, BG0843 and BG0845, which make it pass.

## Acceptance Criteria

- [ ] **AC1** Given a committed git fixture shaped like the rehearsal's v4.1 project, when `migrate.py --apply --format json` runs, the apply is committed, and `gate.py --format json` runs, then the gate's failing blocking lanes include reconcile, conformance, validate and engagement-floor (asserted, so the test cannot pass on a fixture that fails none), and for every failing blocking lane the gate reports, a migrate item carries that lane in its `lane` field with the gate's count. Fails on: HEAD, where no migrate item carries a lane, reconcile disagrees (2 against the gate's count) and the engagement floor is unnamed; and on a run that skips the commit, where conformance and validate pass on the diff and go uncompared
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_gate_agree.py::MigrateGateAgreeTests::test_migrate_names_every_lane_the_gate_fails
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given the same fixture as a git repository with no sdlc-studio/.gitignore, after both runs `git status --porcelain` names no path under sdlc-studio/.local. Fails on: HEAD, where gate.py leaves gate-cost.json untracked (BG0844)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_gate_agree.py::MigrateGateAgreeTests::test_migrate_then_gate_leaves_no_runtime_state_in_git_status
  - **Verified:** yes (2026-09-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Finalised by hand after goal-review round 79 (two-round limit): migrate items gain a `lane` field (migrate.py and project_upgrade.py in Affects, points 2 to 3, engineering seat); the fixture is committed before the gate runs, since a dirty tree scopes conformance and validate to the diff (product and engineering seats); AC1 asserts the four lanes appear and counts blocking lanes only (QA seat). |
