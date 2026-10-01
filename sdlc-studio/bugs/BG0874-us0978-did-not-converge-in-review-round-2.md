# BG0874: US0978 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/help/handoff.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T16:04:02Z

## Summary

US0978 was rejected at round 2, the review cap, by qa-seat reviewer (subagent a1c1c81c), so it was carried as a known issue rather than reviewed again. The findings still open: [new] OVER-CLAIMED repair of round-1 finding 5: sdlc-studio/prd.md:274 (Quality gate row) still reads plus bound close lanes (retro, lessons, review currency, handoff), false since gate.py lost its handoff bound lane in 4ebc34b8 - repro grep -n 'review currency, handoff' sdlc-studio/prd.md; [new] minor: the inline comment in WorklistTests::test\_sprint\_plan\_refuses\_cleanly\_on\_an\_unreadable\_run\_state says the guard is the only thing between --write and the wreckage being overwritten, false - open\_run's own read raises, the guard buys a clean exit 2 instead of a traceback; [pre-existing] sdlc-studio/prd.md:395 lists handoff as a close-chain step, made false by US0967; [pre-existing] a v3-keyed HO file reports orphan-row (BG0873); [pre-existing] gate conformance names US0357 and US0358 missing verified in a clone without markdownlint, environmental

## Steps to Reproduce

1. Read the round 2 REJECT of US0978 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0978 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [new] OVER-CLAIMED repair of round-1 finding 5: sdlc-studio/prd.md:274 (Quality gate row) still reads plus bound close lanes (retro, lessons, review currency, handoff), false since gate.py lost its handoff bound lane in 4ebc34b8 - repro grep -n 'review currency, handoff' sdlc-studio/prd.md
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] minor: the inline comment in WorklistTests::test\_sprint\_plan\_refuses\_cleanly\_on\_an\_unreadable\_run\_state says the guard is the only thing between --write and the wreckage being overwritten, false - open\_run's own read raises, the guard buys a clean exit 2 instead of a traceback
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [pre-existing] sdlc-studio/prd.md:395 lists handoff as a close-chain step, made false by US0967
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** The round 2 REJECT finding no longer holds: [pre-existing] a v3-keyed HO file reports orphan-row (BG0873)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC5** The round 2 REJECT finding no longer holds: [pre-existing] gate conformance names US0357 and US0358 missing verified in a clone without markdownlint, environmental
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC6** US0978 AC1 still passes: Given the shipped CLIs, when `gate.py --require-handoff HO0001` and `artifact.py new --type handoff --title x --dry-run` run, then both exit 2 as unknown, `handoff.py --help` lists no `generate` verb, and `reference-sprint.md` names no handoff the close writes. Fails on: HEAD accepts `--require-handoff` (gate.py:2803), `artifact.py new --type handoff --dry-run` would create HO-0094, and reference-sprint.md:187 reads "The close writes a handoff for every run"
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py::ReportReplacesHandoffTests::test_the_handoff_writers_and_gate_are_retired
- [ ] **AC7** US0978 AC2 still passes: Given a fixture holding an HO file and its `handoffs/_index.md` row from before this change, when `reconcile.py detect` runs, then it exits 0 reporting no handoff drift and both files are byte-identical afterwards. Fails on: a deletion that drops `handoff` from `sdlc_md.ARTIFACT_TYPES`, which orphans the 94 HO files already in this repository
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py::ReportReplacesHandoffTests::test_old_handoffs_stay_readable_and_unrewritten

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
