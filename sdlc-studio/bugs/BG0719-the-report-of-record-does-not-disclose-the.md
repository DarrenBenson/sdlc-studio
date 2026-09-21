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

- [ ] **AC1: a waiver in force for the run appears in the report.**
  - **Given** a decision that stands a gate down, dated inside the run's window
  - **When** the report of record is derived
  - **Then** it carries a waivers set naming that decision id, the lane or row stood down, and the dated reason - the signer is told which gate was not holding when they sign
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_waiver_in_force_is_disclosed_with_its_lane_and_reason
- [ ] **AC2: a decision that waives nothing is not listed as a waiver.**
  - **Given** an ordinary design decision inside the same window
  - **When** the report derives its waivers
  - **Then** it is absent - the discriminating half, because listing every decision would disclose nothing and bury what matters
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_an_ordinary_decision_is_not_a_waiver
- [ ] **AC3: the waiver window is the same bound the DORA figures use.**
  - **Given** a waiver dated AFTER the report's `window_end`
  - **When** the report is re-derived from the same page
  - **Then** it is excluded, so a decision taken later cannot move a signed figure - the scar this repo already paid for once in BG0718
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_waiver_after_the_window_end_cannot_move_a_signed_page
- [ ] **AC4: a run with no waivers says so rather than omitting the section.**
  - **Given** a run in whose window no waiver was recorded
  - **When** the report renders
  - **Then** the waivers set is present and empty - an absent section reads as "not checked", and the whole point is that the signer can tell the difference
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_run_with_no_waivers_renders_an_explicit_empty_set

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint_report.py`, omit the waivers derivation from the report payload entirely - the shipped behaviour, under which RPT0002 was signed with two waivers in force and named neither | a waiver in force is disclosed |
| AC2 | in `sprint_report.py`, collect every decision inside the window as a waiver rather than testing it for a waiver subject | an ordinary decision is not a waiver |
| AC3 | in `sprint_report.py`, bound the waiver derivation by the current time instead of the report's recorded `window_end` | a later waiver cannot move a signed page |
| AC4 | in `sprint_report.py`, drop the waivers key from the payload when the derived set is empty | an empty set is explicit |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-19 | sdlc-studio | Filed |
| 2026-09-20 | operator ruling | D0223: delivered in the BUILD run alongside D0218's close-and-ruling-ergonomics theme, not in the sweep. It shares a surface and a reviewer with CR0571 (a carried ruling is not checked against who may rule) and CR0576 (the release cut does not list rulings carried since the last tag); the three are one claim about what a close discloses and to whom. Stays open and disclosed meanwhile. |
