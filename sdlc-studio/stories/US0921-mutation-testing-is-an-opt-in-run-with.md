# US0921: The gate carries no mutation lane

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py, changelog.d/US0921.md, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_gate_lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, tools/tests/test_test_census.py, sdlc-studio/stories/US0054-gate-wiring-and-docs-advisory-mutation-lane-discipline.md, sdlc-studio/stories/US0216-gate-mutation-lane-surfaces-the-refused-red-baseline.md, sdlc-studio/stories/US0302-artefacts-filed-from-survivors-link-back-so-yield.md, sdlc-studio/stories/US0379-mutation-py-records-an-empty-surface-as-a.md
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who runs mutation testing only when she wants to probe a suite
**I want** the gate to carry no `mutation` lane, on demand or advisory, and an upgrade to stop announcing one
**So that** mutation testing is an instrument she picks up, not a lane the gate reads and an upgrade tells her to feed

## Acceptance Criteria

- **AC1:** Given `gate.py --only mutation`, when invoked, then it is refused as no gate lane; `ON_DEMAND_CHECKS` and `ADVISORY_WHEN_ABSENT` hold no `mutation` and `_mutation_coverage` is gone; an open rewrite window claiming a staged path is still refused by the `window` lane, which stays. Fails on: HEAD, where `mutation` is an on-demand lane, and on a deletion that takes the `window` lane with it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_no_mutation_lane_and_the_window_still_guards
- **AC2:** Given `project_upgrade.new_advisory_lanes("2.5.0", "3.4.0")`, the version gap in which the mutation lane arrived, then it names no `mutation` lane and directs no one to create a mutation report. Fails on: removing the lane from the gate while `ADVISORY_WHEN_ABSENT` still lists it for the upgrade digest
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_opt_in.py::MutationOptInTests::test_an_upgrade_announces_no_mutation_lane

## Notes

- Split from the original US0921 (5 points) as its "a" half: the old AC3 as amended. The ledger verbs, `run` without a ledger, the brief and close reads and the stamps moved to US0936.
- The old AC3 as first written already passed at HEAD: `mutation` has been an on-demand lane since US0895. The amended form fails at HEAD.
- Stamps: none measured. MutationLaneTests, MutationCoverageTests, MutationProvenanceTests, MutationRefusedLaneTests and `AdvisoryLaneTests::test_mutation_lane_named_in_gap` carry no stamped selector.
- Engineering call: this half keeps the original module `test_lean_mutation_opt_in.py` and its AC3 selector. US0936 gets a new module.
- `gate.py` lines 380-640. Lands before US0936.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: split 5 -> 3 + 8 (US0936 takes the ledger verbs); retitled to the gate's mutation lane; user story rewritten for this half; AC1 is the old AC3 amended so it fails at HEAD; new AC2 for the upgrade digest; stamps measured at none; Affects narrowed to gate.py, project_upgrade.py, their tests, help/gate.md and the changelog fragment |
