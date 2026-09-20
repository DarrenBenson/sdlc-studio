# BG0719: the report of record does not disclose the waivers that permitted the seal, so an operator signs without being told which gate stood down

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

RPT0002 was signed for RUN-01M2SPNS while two decisions were in force that made the seal possible, and the page names neither. D0214 stood `review.line_coverage` down from `block` to `report` FOR THAT SEAL ONLY, because BG0706 charges every unit with its batch siblings' added lines; D0215 waived the close checklist's known-issues row. The page carries a `Not proven` section whose stated purpose is 'what this run did not establish, as a section rather than an omission' - and it lists one item, the per-unit token split, while the stood-down coverage gate is absent. A reader of the signed page cannot tell that the per-unit coverage evidence the confidence profile implies was never required. The decisions exist, are dated and are properly recorded in `sdlc-studio/decisions.md`; what is missing is the join from the report of record to the waivers that were live when it was derived, which is exactly the join a signature is supposed to freeze.

## Steps to Reproduce

1. Record a decision that stands a close-gate lane down for a run, as D0214 does. 2. Close and seal the run. 3. Read the filed report: grep it for the decision id, for 'waiv', or for the lane's name. Nothing. 4. Read its `Not proven` section: the stood-down lane is not among the items. Observed on RPT0002, fingerprint 215a0147800b237e, signed 2026-09-19.

## Proposed Fix

Derive a waivers row set from `sdlc-studio/decisions.md` scoped to the run - the decisions whose text names the run id, or which are dated inside the run window and carry a waiver subject - and render them in `Not proven` beside the measurement gaps, each with its decision id, the lane or row it stands down, and its dated reason. The figures must be sourced to decisions.md like every other figure. Take care with the digest: a decision recorded after the page is derived would move a signed figure, so scope the derivation to the same window bound the DORA figures use, which BG0718 has just made reliable.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: RPT0002 was signed for RUN-01M2SPNS while two decisions were in force that made the seal possible, and the page names neither.
- [ ] **AC2** The proposed fix lands, pinned by a test: Derive a waivers row set from `sdlc-studio/decisions.md` scoped to the run - the decisions whose text names the run id, or which are dated inside the run...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-19 | sdlc-studio | Filed |
| 2026-09-20 | operator ruling | D0223: delivered in the BUILD run alongside D0218's close-and-ruling-ergonomics theme, not in the sweep. It shares a surface and a reviewer with CR0571 (a carried ruling is not checked against who may rule) and CR0576 (the release cut does not list rulings carried since the last tag); the three are one claim about what a close discloses and to whom. Stays open and disclosed meanwhile. |
