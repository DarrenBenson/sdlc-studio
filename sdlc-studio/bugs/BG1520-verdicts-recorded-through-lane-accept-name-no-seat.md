# BG1520: Verdicts recorded through lane accept name no seat, so the seat learning loop has never been fed

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/templates/personas/memory-template.md memory-template.md (whole file, the store `persona_memory.py` seeds) and sdlc-studio/personas/seats/*.md; observed in sdlc-studio/retros/RETRO0146 line 111, RETRO0147 line 119, RETRO0148 line 104
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:21:55Z

## Summary

The persona learning loop keys each learning to a seat through the parenthesised role in a ledger Reviewer cell, read by `recorded_seat` in `critic.py`. This repository's runs record reviewers through `sprint.py lane accept --reviewer`, which takes free text of the form qa-seat-UNIT-r1 with no parenthesised role, so `recorded_seat` returns nothing for every row. `learnings_review` in `retro.py` builds its list of seats owing a learning only from attributed rows, so with none attributed no seat is ever listed as owing one. Three runs have closed since the feature shipped: their retros report 21 of 21, 24 of 24 and 11 of 11 verdict rows naming no seat, the personas memory folder does not exist, and each close reads as a clean result. The failure is silent, because the count is printed but nothing refuses or files it.

## Steps to Reproduce

1. Run retro.py seats with --id RETRO0148: it prints that 11 of 11 verdict rows name no seat, each reviewer reading like qa-seat-UNIT-r1.
2. Repeat for RETRO0146 and RETRO0147: 21 of 21 and 24 of 24 rows name no seat.
3. List sdlc-studio/personas/memory: the folder does not exist.
4. Read `_RECORDED_SEAT` and `recorded_seat` in .claude/skills/sdlc-studio/scripts/critic.py (about lines 2622 to 2637): only a parenthesised role is read as a seat.
5. Read the `--reviewer` argument of lane accept in sprint.py and line 38 of reference-sprint-toolchain.md: the value is free text, while line 55 documents the holder and role form for `critic.py record`.

## Proposed Fix

Make the lane path attribute a seat. Have lane accept write the Reviewer cell in the holder and role form, taking the role from the seat the reviewer was briefed with, and refuse a `--reviewer` value that carries no known seat when the brief named one. Make the retro's learnings review report a run whose verdict rows are wholly unattributed as owed and not as clean. Correct the lane accept row in the toolchain runbook. Pin the attribution, the refusal and its positive control in the lane accept and retro learning tests.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The persona learning loop keys each learning to a seat through the parenthesised role in a ledger Reviewer cell, read by `recorded_seat` in `critic.py`.
- [ ] **AC2** The proposed fix lands, pinned by a test: Make the lane path attribute a seat.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
