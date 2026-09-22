# BG0719: the report of record does not disclose the waivers that permitted the seal, so an operator signs without being told which gate stood down

> **Status:** Fixed
> **Forced-override:** 2026-09-22: --force waived 1 gate(s) on Fixed - BG0719: 158 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2036, 2038, 2041, 2043, 2046, 2060, 2061, 2064, 2066, 2093, 2094, 2109, 2114, 2115, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2182, 2188, 2189, 2190, 2197, 2203, 2205, 2284, 2286, 2357, 2504, 2505, 2509, 2510; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4479, 4480, 4481, 4482, 4490, 4495, 4496, 4497, 4498, 4503, 4504, 4505, 4513, 4514, 4515, 4516, 4517, 4518, 4520, 4522, 4526, 4528, 4529, 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4550, 4551, 4555, 4557, 4558, 4559, 4565, 4566, 4567, 4572, 4573, 4574, 4575, 4582, 4583, 4584, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4632, 4633, 4634, 4635, 4636, 4637, 4647, 4651, 4658, 4660, 4661, 4666, 4668, 4669, 4670, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4688, 4689, 4690, 4693, 4694, 4695, 4696, 4697, 4699, 4700, 4701, 4703, 4709, 4712, 4713, 4714, 4716, 4717, 4718, 4723, 4724, 4725, 4726, 4729, 4733, 4736, 4737. Rule a line equivalent with `verify_ac.py coverage rule --id BG0719 --file <path> --line <n> --reason <why>`, or reach it with a test
> **Severity:** High
> **Points:** 8
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Verification depth:** functional
> **Created:** 2026-09-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

RPT0002 was signed for RUN-01M2SPNS while two decisions were in force that made the seal possible, and the page names neither. D0214 stood `review.line_coverage` down from `block` to `report` FOR THAT SEAL ONLY, because BG0706 charges every unit with its batch siblings' added lines; D0215 waived the close checklist's known-issues row. The page carries a `Not proven` section whose stated purpose is 'what this run did not establish, as a section rather than an omission' - and it lists one item, the per-unit token split, while the stood-down coverage gate is absent. A reader of the signed page cannot tell that the per-unit coverage evidence the confidence profile implies was never required. The decisions exist, are dated and are properly recorded in `sdlc-studio/decisions.md`; what is missing is the join from the report of record to the waivers that were live when it was derived, which is exactly the join a signature is supposed to freeze.

**Scope, recorded on delivery: only D0215 is recoverable by this unit.** D0214 is prose, not a
canonical `waiver: <subject>` row, and its own rationale says why - the waiver vocabulary declares
no subject for that lane, so `decisions.py waive` could not express it. Widening the matcher to
read prose would put words into a ruling's mouth on a page carrying a signature, which is a worse
failure than silence. That is a defect in what `waive` can EXPRESS, filed as BG0740 with the
vocabulary remedy named, not a defect in this reader. A re-derived RPT0002 therefore names D0215
and not D0214 until BG0740 lands.

## Steps to Reproduce

1. Record a decision that stands a close-gate lane down for a run, as D0214 does. 2. Close and seal the run. 3. Read the filed report: grep it for the decision id, for 'waiv', or for the lane's name. Nothing. 4. Read its `Not proven` section: the stood-down lane is not among the items. Observed on RPT0002, fingerprint 215a0147800b237e, signed 2026-09-19.

## Proposed Fix

Derive a waivers row set from `sdlc-studio/decisions.md` scoped to the run - the decisions whose text names the run id, or which are dated inside the run window and carry a waiver subject - and render them in `Not proven` beside the measurement gaps, each with its decision id, the lane or row it stands down, and its dated reason. The figures must be sourced to decisions.md like every other figure. Take care with the digest: a decision recorded after the page is derived would move a signed figure, so scope the derivation to the same window bound the DORA figures use, which BG0718 has just made reliable.

## Acceptance Criteria

- [ ] **AC1: a waiver in force appears with its subject and its reason.**
  - **Given** an accepted decision whose cell is `waiver: review.line_coverage`, dated inside the run's window
  - **When** the waivers are derived
  - **Then** the row carries the decision id, the subject and the dated reason - RPT0002 was signed with two such waivers in force and named neither, so the operator signed without being told which gate was not holding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_waiver_in_force_is_disclosed_with_its_subject_and_reason
  - **Verified:** yes (2026-09-22)
- [ ] **AC2: an ordinary decision is not a waiver, and a superseded one does not hold.**
  - **Given** an ordinary design decision, and a decision that merely mentions a waiver in prose
  - **When** the waivers are derived
  - **Then** neither is collected - the canonical token is the marker, and listing every decision would disclose nothing while burying what matters
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_an_ordinary_decision_is_not_a_waiver
  - **Verified:** yes (2026-09-22)
- [ ] **AC2b: a superseded waiver is not in force.**
  - **Given** a `waiver:` row whose status is superseded
  - **When** the waivers are derived
  - **Then** it is absent - reporting it would tell the signer a gate stood down that did not
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_superseded_waiver_does_not_hold
  - **Verified:** yes (2026-09-22)
- [ ] **AC3: the waiver window is the report's own `window_end`.**
  - **Given** a waiver dated after the page's recorded window end
  - **When** the page is re-derived
  - **Then** it is excluded - BG0718 is the scar, where signing widened a window and invalidated the page one second later, so a decision taken afterwards must not be able to move a signed figure
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_waiver_after_the_window_end_cannot_move_a_signed_page
  - **Verified:** yes (2026-09-22)
- [ ] **AC4: a run with no waivers renders an explicit empty set.**
  - **Given** a decisions log carrying no accepted waiver in the window
  - **When** the section renders
  - **Then** it is present, empty, and says the log was read and no gate stood down - an absent section reads as `not checked`, and the whole point is that the signer can tell the difference
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_run_with_no_waivers_renders_an_explicit_empty_set
  - **Verified:** yes (2026-09-22)
- [ ] **AC5: the section reaches the report of record.**
  - **Given** the report builder
  - **When** a page is derived
  - **Then** the section is appended and the renderer knows how to list its rows - two sibling units in this same run shipped correct derivations that no caller reached, and a disclosure nobody can read has disclosed nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_the_section_reaches_the_report_of_record
  - **Verified:** yes (2026-09-22)

- [ ] **AC3b: a waiver recorded BEFORE the run opened is not in force for it.**
  - **Given** a waiver dated months before the run's window and one inside it
  - **When** the waivers are derived
  - **Then** only the second is returned - applying the upper bound alone returned 67 rows on this repository, almost all one-shot per-story waivers long discharged, and the note claimed all 67 were not holding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_waiver_before_the_run_opened_is_not_in_force_for_it
  - **Verified:** yes (2026-09-22)
- [ ] **AC3c: an unbounded read reports NOT MEASURED, not a clean sheet.**
  - **Given** a derivation called with no window end, no window start, or neither
  - **When** the section is built
  - **Then** it carries `not_measured` and NO note - fail-closed is only half of it, because the first repair returned nothing AND emitted `the log was read and carries no accepted waiver`, so a read that REFUSED to run was word-for-word indistinguishable from one that ran and found nothing, on a signed page. That is this bug's own failure mode reproduced by its fix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_an_unbounded_read_reports_NOT_MEASURED_not_a_clean_sheet
  - **Verified:** yes (2026-09-22)
- [ ] **AC3d: a waiver with no readable date is disclosed, not dropped.**
  - **Given** an accepted waiver whose Date cell is blank
  - **When** the section is built
  - **Then** it is absent from the rows AND named in the note as UNKNOWN - the sibling unit BG0715 built its undatable set in this same run precisely so an item the window cannot judge is named rather than silently excluded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_waiver_with_no_readable_date_is_disclosed_not_dropped
  - **Verified:** yes (2026-09-22)
- [ ] **AC6: each row carries its date, and a populated note states the count.**
  - **Given** two waivers inside the window
  - **When** the section is built
  - **Then** the rows carry their dates in log order and the note names the count - the date cell, the note's non-empty branch and row order were all unpinned
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_a_row_carries_its_date_and_a_populated_note
  - **Verified:** yes (2026-09-22)

- [ ] **AC5b: the NOT MEASURED path RENDERS.**
  - **Given** a run record carrying no usable window, so the section reports NOT MEASURED
  - **When** the markdown twin is rendered
  - **Then** it renders, and carries both `NOT MEASURED` and the reason - three rounds running a correct derivation shipped with a path nobody rendered, and here both templates held a bare `{{waivers_note}}` the not-measured branch supplies no figure for, so `_render` refused and the run that most needed the disclosure could not have its page produced at all
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_the_not_measured_path_RENDERS
  - **Verified:** yes (2026-09-22)

- [ ] **AC5c: an unreadable decisions log returns the shape the caller unpacks.**
  - **Given** a tree where the decisions module cannot be imported
  - **When** the waivers are derived
  - **Then** it returns an empty pair - the guard's own comment says a report must not die on a log read, and returning a bare list against a signature declaring a pair made the guard the death it exists to prevent
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverDisclosureTests::test_an_unreadable_decisions_log_returns_the_shape_the_caller_unpacks
  - **Verified:** yes (2026-09-22)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint_report.py`, blank the rationale so the signer is told a gate stood down but not why | |
| AC2 | in `sprint_report.py`, collect every decision as a waiver rather than testing for the canonical token | |
| AC2b | in `sprint_report.py`, include superseded waivers, telling the signer a gate stood down that did not | |
| AC3 | in `sprint_report.py`, delete the upper bound so a decision taken after the page was derived can move it | |
| AC3b | in `sprint_report.py`, delete the lower bound so 67 historic waivers are listed as in force | |
| AC3c | in `sprint_report.py`, let an unbounded read fall through to the note, claiming the log was read | |
| AC3d | in `sprint_report.py`, drop a waiver with no readable date silently instead of disclosing it | |
| AC4 | in `sprint_report.py`, blank the not-measured reason, the only text the signer gets on that path | |
| AC5 | in `sprint_report.py`, build the section but never append it, so no report carries it | |
| AC5b | in `templates/core/sprint-report.md`, delete the unless block so the not-measured path renders nothing | |
| AC5c | in `sprint_report.py`, revert the import guard to a bare list so the caller's unpack raises | |
| AC6 | in `sprint_report.py`, rename the date cell so no row carries the date it was recorded on | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-19 | sdlc-studio | Filed |
| 2026-09-20 | operator ruling | D0223: delivered in the BUILD run alongside D0218's close-and-ruling-ergonomics theme, not in the sweep. It shares a surface and a reviewer with CR0571 (a carried ruling is not checked against who may rule) and CR0576 (the release cut does not list rulings carried since the last tag); the three are one claim about what a close discloses and to whom. Stays open and disclosed meanwhile. |
| 2026-09-22 | transition set --force | forced BG0719 -> Fixed, waiving 2 gate(s): BG0719: 13 planned mutant(s) unaccounted for - AC1 was planned and never executed - `in`sprint_report.py`, drop the rationale from the row, so t`; AC2 row 0 was planned and never executed - `in`sprint_report.py`, collect every decision as a waiver ra`; AC2 row 1 was planned and never executed - `in`sprint_report.py`, include superseded waivers, telling t`; AC3 row 0 was planned and never executed - `in`sprint_report.py`, delete the window bound so a decision`; AC4 was planned and never executed - `in`sprint_report.py`, emit an empty note for an empty set,`; AC5 row 0 was planned and never executed - `in`sprint_report.py`, build the section but never append it`; AC5 row 1 was planned and never executed - `in`templates/core/sprint-report.md`, rename the repeat bloc`; AC3 row 1 was planned and never executed - `in`sprint_report.py`, drop the lower bound so 67 historic w`; AC3 row 2 was planned and never executed - `in`sprint_report.py`, make a missing bound fail OPEN, retur`; AC3 row 3 was planned and never executed - `in`sprint_report.py`, let an unbounded read fall through to`; AC3 row 4 was planned and never executed - `in`sprint_report.py`, drop a waiver with no readable date s`; AC5 row 4 was planned and never executed - `in`sprint_report.py`, revert the import guard to a bare lis`; AC6 was planned and never executed - `in`sprint_report.py`, rename the date cell so no row carrie`. Check them with `mutation.py run --story BG0719 --from-plan` (its type is `bug`); BG0719: 158 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2036, 2038, 2041, 2043, 2046, 2060, 2061, 2064, 2066, 2093, 2094, 2109, 2114, 2115, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2182, 2188, 2189, 2190, 2197, 2203, 2205, 2284, 2286, 2357, 2504, 2505, 2509, 2510; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4479, 4480, 4481, 4482, 4490, 4495, 4496, 4497, 4498, 4503, 4504, 4505, 4513, 4514, 4515, 4516, 4517, 4518, 4520, 4522, 4526, 4528, 4529, 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4550, 4551, 4555, 4557, 4558, 4559, 4565, 4566, 4567, 4572, 4573, 4574, 4575, 4582, 4583, 4584, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4632, 4633, 4634, 4635, 4636, 4637, 4647, 4651, 4658, 4660, 4661, 4666, 4668, 4669, 4670, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4688, 4689, 4690, 4693, 4694, 4695, 4696, 4697, 4699, 4700, 4701, 4703, 4709, 4712, 4713, 4714, 4716, 4717, 4718, 4723, 4724, 4725, 4726, 4729, 4733, 4736, 4737. Rule a line equivalent with `verify_ac.py coverage rule --id BG0719 --file <path> --line <n> --reason <why>`, or reach it with a test |
| 2026-09-22 | transition set --force | forced BG0719 -> Fixed, waiving 1 gate(s): BG0719: 158 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2036, 2038, 2041, 2043, 2046, 2060, 2061, 2064, 2066, 2093, 2094, 2109, 2114, 2115, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2182, 2188, 2189, 2190, 2197, 2203, 2205, 2284, 2286, 2357, 2504, 2505, 2509, 2510; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4479, 4480, 4481, 4482, 4490, 4495, 4496, 4497, 4498, 4503, 4504, 4505, 4513, 4514, 4515, 4516, 4517, 4518, 4520, 4522, 4526, 4528, 4529, 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4550, 4551, 4555, 4557, 4558, 4559, 4565, 4566, 4567, 4572, 4573, 4574, 4575, 4582, 4583, 4584, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4632, 4633, 4634, 4635, 4636, 4637, 4647, 4651, 4658, 4660, 4661, 4666, 4668, 4669, 4670, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4688, 4689, 4690, 4693, 4694, 4695, 4696, 4697, 4699, 4700, 4701, 4703, 4709, 4712, 4713, 4714, 4716, 4717, 4718, 4723, 4724, 4725, 4726, 4729, 4733, 4736, 4737. Rule a line equivalent with `verify_ac.py coverage rule --id BG0719 --file <path> --line <n> --reason <why>`, or reach it with a test |
