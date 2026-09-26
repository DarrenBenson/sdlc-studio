# BG0785: migrate leaves a v4-era project's conformance lane red on its pre-adoption stories and names no cutoff for them

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, tools/rehearse-release.sh, tools/release-rehearsal-baseline.txt, .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py
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

- [ ] **AC1** The behaviour described is corrected: A v4-era project upgraded with `migrate --apply` fails the gate's conformance lane on every pre-adoption unit (stories written before executable criteria...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `bash tools/rehearse-release.sh upgrade`: the rehearsal passes only because the baseline row `upgrade|conformance|...` tolerates the red lane.
- [ ] **AC3** The proposed fix lands, pinned by a test: migrate reports, as a needs-a-human item, the pre-adoption units the conformance lane would fail and the `conformance.adopt_after` line that grandfathers them...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
