# BG0516: the close reports a gate refusal it could not attribute, where the gate named its failing lane plainly

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Observed on RUN-01KZ5YXM's close on 2026-08-04 across four consecutive attempts, each recorded in run-state `close_attempts` with `outstanding: 1, stages: [gate]`. The gate's own output at the same moment: `[FAIL] review-current [124.9s]: reviews/LATEST.md is stale - 15 artefact(s) changed since the last review (BG0513, BG0514, BG0515, CR0528, CR0529, CR0530, CR0531, SC0001, US0487, US0488 (+5 more))`.
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint close` runs `gate --require-retro <id> --require-review` and passes its output to `close_blocker_split`. When the split cannot attribute the refusal it reports `close gate: the refusal could not be attributed - its verdict named no failing lane this close can read, so it is treated as a blocker in the WORK`, and stops.

On RUN-01KZ5YXM's close this fired four times in a row while the gate's own output named the lane in terms: `[FAIL] review-current [124.9s]: reviews/LATEST.md is stale - 15 artefact(s) changed since the last review ... run review before closing`. The operator is told the refusal cannot be identified by the very command that just printed its identity.

The cost is not one message. The close's own loop guard counts attempts and the outstanding set never shrank - four rounds all recorded `outstanding: 1, stages: [gate]` - so the run hit `LOOP STOPPED: the declared round cap of 4 is reached` and quarantined itself. An unattributable refusal is unfixable by construction, so every retry looks identical to the guard and the cap is reached without a single real attempt at the actual blocker. Running `gate.py --require-retro <id>` by hand exits 0, which sends a reader looking in the wrong place; the `--require-review` form is the one that fails, and only the close passes that flag.

## Steps to Reproduce

1. Open a run, deliver its units, write and validate a retro.
2. Let `reviews/LATEST.md` go stale (any artefact change since the last review does it).
3. `sprint.py close --retro RETROxxxx` - it stops with `the refusal could not be attributed`.
4. `gate.py --require-retro RETROxxxx` alone - exit 0, every lane passes.
5. `gate.py --require-retro RETROxxxx --require-review` - `[FAIL] review-current`, named clearly.
6. Retry step 3 four times; each records `outstanding: 1, stages: [gate]` and the fourth trips the loop cap.

## Proposed Fix

Make `close_blocker_split` recognise the `review-current` lane, and - more importantly - make the unattributed branch print what the gate actually said rather than reporting that it said nothing. A refusal the close cannot classify is still a refusal whose text it holds: the honest message names the lane the gate named and says only the CLASSIFICATION failed. Consider also not counting an unattributed round against the loop cap, since a round the operator cannot act on is not an attempt.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `sprint close` runs `gate --require-retro <id> --require-review` and passes its output to `close_blocker_split`.
- [ ] The proposed fix lands, pinned by a test: Make `close_blocker_split` recognise the `review-current` lane, and - more importantly - make the unattributed branch print what the gate actually said rather...

## Impact

A gate that refuses without saying what refused you is worse than the flake it is reporting - it is the same shape as BG0513, one layer up. Here it also burns the loop guard: the close quarantines itself after four rounds that were never real attempts, and the run cannot be closed by the command built to close it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
