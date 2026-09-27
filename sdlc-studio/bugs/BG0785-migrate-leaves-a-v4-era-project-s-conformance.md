# BG0785: migrate leaves a v4-era project's conformance lane red on its pre-adoption stories and names no cutoff for them

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, tools/rehearse-release.sh, tools/release-rehearsal-baseline.txt, .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py, changelog.d/BG0785.md
> **Evidence:** US0938: `tools/rehearse-release.sh upgrade` on a v4-era fixture (US0001 Done, US0002 Ready, neither with a Verify line): migrate reports 2 applied and 3 needing a human, none about conformance; `gate.py` then fails conformance with 2 non-conformant units and names `conformance.adopt_after` as its remedy
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T12:26:58Z

## Summary

A v4-era project upgraded with `migrate --apply` fails the gate's conformance lane on every pre-adoption unit (stories written before executable criteria, Verify lines or recorded verdicts existed), and migrate's report says nothing about it: the upgrader learns of the grandfathering decision from a red gate, not from the upgrade. `conformance.adopt_after` is the shipped remedy, but choosing its value is a judgement about the project's history, so migrate should propose the cutoff as a needs-a-human item with the exact line to add, never write it. This is the known gap `tools/release-rehearsal-baseline.txt` tolerates for the `upgrade` path; CR0497, its previous owner, was retired by D0265 with 'v6 migrate instead', so the gap had no open owner.

## Steps to Reproduce

Run `bash tools/rehearse-release.sh upgrade`: the rehearsal passes only because the baseline row `upgrade|conformance|...` tolerates the red lane. Read migrate's report in the fixture: no needs-a-human item names the pre-adoption units or a cutoff.

## Proposed Fix

migrate reports, as a needs-a-human item, the pre-adoption units the conformance lane would fail and the `conformance.adopt_after` line that grandfathers them (the highest such id), without writing it. The rehearsal then applies that named line as the upgrader would, the conformance lane reports the units exempt (pre-adoption), and the `upgrade|conformance` row leaves the baseline in the same commit.

## Acceptance Criteria

- [ ] **AC1** Given the rehearsal's v4-era fixture (US0001 Done and US0002 Ready, neither with a Verify line, no `conformance.adopt_after`), when `migrate.py` runs dry and then with `--apply`, then both reports carry one needs-a-human item naming the units the conformance lane would fail and the exact line `conformance.adopt_after: US0002` that grandfathers them, and `sdlc-studio/.config.yaml` is byte-identical afterwards. Fails on: HEAD (no such item; measured through `tools/rehearse-release.sh upgrade`); migrate writing the cutoff itself; naming a cutoff below a failing unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::ConformanceCutoffTests::test_migrate_names_the_cutoff_and_writes_nothing
  - **Verified:** yes (2026-09-27)
- [ ] **AC2** Given a project whose `conformance.adopt_after` already covers every unit the lane would fail (the shape of a real v4.1 project that set 179), when `migrate.py` runs, then no cutoff item is reported. Fails on: proposing a cutoff unconditionally, or proposing one that lowers an existing cutoff
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::ConformanceCutoffTests::test_an_existing_covering_cutoff_is_left_alone
  - **Verified:** yes (2026-09-27)
- [ ] **AC3** Given `tools/rehearse-release.sh upgrade`, when the rehearsal applies the line migrate named, as an upgrader would, then the gate's conformance lane passes with the units reported exempt (pre-adoption), and `tools/release-rehearsal-baseline.txt` carries no `upgrade|conformance` row. Fails on: leaving the baseline row (the rehearsal reddens in the other direction), or a rehearsal that hard-codes the cutoff rather than reading it from migrate's report
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py::UpgradeRehearsalTests::test_the_upgrade_gates_green_on_the_cutoff_migrate_names
  - **Verified:** yes (2026-09-27)

## Notes

- - 2026-09-27 (QA seat, Sprint 6 planning): reproduced at HEAD f76b70cc: `bash tools/rehearse-release.sh upgrade` passes only on the `upgrade|conformance|BG0785` baseline row. On a scratch clone of a real v4.1 project the conformance lane passed because it already sets `adopt_after: 179`, hence AC2. Out of scope and filed separately: `parse_cutoff` refuses every ULID id, so a schema v3 project cannot use the remedy the gate names (see qa-new.json). The engagement-floor lane has its own cutoff and is not part of this bug.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | QA seat: groomed for Sprint 6 - three lean criteria; AC2 added from a real v4.1 project that already carries a cutoff |
