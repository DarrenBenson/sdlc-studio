# BG0620: eighteen units carry a REJECT no repair record answers, so the fingerprint-keyed roll-up BG0607 needs cannot land until their evidence is backfilled

> **Status:** Superseded
> **Superseded by:** BG0607. Two independent pre-code goal reviews proved these cannot be separate units. `record_repair` refuses a unit carrying no live REJECT, and under the shipped roll-up all nineteen read APPROVE - verified directly, 19/19 - so the backfill is not recordable until BG0607's code ships. BG0607's own lane-green criterion is meanwhile not satisfiable until the backfill lands. The dependency as filed was inverted. Its criteria are now BG0607 AC5, AC6 and AC7, with the undecidable question of whether any finding was unrepaired replaced by a reported closed-versus-filed split and a fixture the checker must fail on.
> **Severity:** Medium
> **Points:** 5
> **Depends on:** BG0618
> **Affects:** sdlc-studio/reviews/repair-record.md
> **Evidence:** Measured 2026-08-26 on the shipped `conformance.py check` from an isolated copy of scripts/ with only `verdict_for` patched. Baseline and probe figures both taken in the same session against the same tree. Five of the 18 sampled by hand and all five are panel splits with no answering repair.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0607 replaces a last-row-wins verdict roll-up with one keyed on the brief fingerprint. Measured on the SHIPPED conformance lane on 2026-08-26 by patching `verdict_for` in an isolated copy of `scripts/` and running `conformance.py check` against this tree: the baseline is 608/690 conformant, 0 not, exit 0, and under the fingerprint rule it is 590/690, 18 not, exit 1. The lane blocks at `--release`, so BG0607 cannot ship alone. The 18 are all stories and they are enumerable: US0577, US0578, US0580, US0583, US0585, US0591, US0597, US0629, US0630, US0631, US0632, US0645, US0662, US0663, US0664, US0665, US0666, US0676. Sampled five of them - each is the exact case BG0607's AC1 describes: one seat REJECTs, a DIFFERENT seat APPROVEs, and no repair record answers the rejection, so the roll-up reads APPROVE on a rejection nobody closed. This unit is that backfill. It is not clerical: each unit needs its REJECT read, the repair that actually answered it identified, and that repair recorded with its evidence.

## Steps to Reproduce

1. Copy `scripts/` to an isolated tree. 2. Patch `verdict_for` so a REJECT stands until a later APPROVE carrying the SAME brief fingerprint retires it. 3. Run `conformance.py check --root <this repo>` from the copy: 590/690, 18 not, exit 1, against a baseline of 608/690, 0 not, exit 0. The 18 non-conformant ids are printed by the lane.

## Proposed Fix

For each of the 18, read the REJECT's findings, establish from the commit history and the unit's own artefact whether they were repaired, and record it with `critic.py repair --unit <id> --closed-file <file>` naming the evidence that closed each finding. Where a finding was NOT in fact repaired, that is a live defect and it is filed rather than papered over - a backfill that records repairs which did not happen is worse than the roll-up it exists to unblock. ORDERING: BG0618 must land FIRST. The repair channel splits its evidence on a bare semicolon and silently discards the remainder, so backfilling 18 units through it before that is fixed would write truncated evidence at scale, into the very records this unit exists to make trustworthy.

## Acceptance Criteria

This unit is SUPERSEDED and holds no criteria of its own. They moved to BG0607 as AC5, AC6 and AC7 when the two were merged, because the backfill is not recordable until BG0607's roll-up ships and BG0607's lane-green criterion is not satisfiable until the backfill lands. Leaving live verifiers here would give one selector two owners, and a regression would fail both without saying which.

## Impact

Without this, BG0607 has only two endings: ship the roll-up and turn a release-blocking lane red on 18 units, which is what happened when it shipped and was withdrawn; or do not ship it, and leave a verdict roll-up decided by the order the recorder was invoked in. With it, BG0607 lands and the 18 rejections that are currently invisible become visible, which is the whole point of the bug.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
