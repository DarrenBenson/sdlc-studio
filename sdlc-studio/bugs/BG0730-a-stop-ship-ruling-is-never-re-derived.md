# BG0730: a stop-ship ruling is never re-derived against its finding's status, so a ruling on a Fixed finding blocks every close permanently

> **Status:** Fixed
> **Forced-override:** 2026-09-22: --force waived 1 gate(s) on Fixed - BG0730: 253 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2043, 2046, 2093, 2094, 2109, 2114, 2115, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2182, 2188, 2189, 2190, 2197, 2203, 2205, 2504, 2505, 2509, 2510, 3426, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3768, 3769, 3770, 3771, 3775, 3780, 3787, 3788, 3792, 3797, 3798, 3801, 3804, 3809; .claude/skills/sdlc-studio/scripts/retro.py: 335; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4479, 4480, 4481, 4482, 4490, 4495, 4496, 4497, 4498, 4503, 4504, 4505, 4513, 4514, 4515, 4516, 4517, 4518, 4520, 4522, 4526, 4528, 4529, 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4550, 4551, 4555, 4557, 4558, 4559, 4565, 4566, 4567, 4572, 4573, 4574, 4575, 4582, 4583, 4584, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4632, 4633, 4634, 4635, 4636, 4637, 4733, 4736, 4737, 4749, 4750, 4751, 4753, 4754, 4758, 4760, 4761, 4762, 4763, 4764, 4765, 4771, 4775, 4780, 4781, 4782, 4790, 4792, 4793, 4800, 4801, 4802, 4803, 4804, 4805, 4807, 4813, 4814, 4815, 4816, 4817, 4819, 4820, 4825, 4826, 4834, 4836, 4840, 4841, 4843, 4844, 4845, 4848, 4849, 4850, 4852, 4854, 4855, 4856, 4857, 4865, 4866, 4869, 4870, 4872, 4873, 4874, 4877, 4878, 4879, 4880, 4881, 4882, 4887, 4894, 4895, 4902, 4904, 4905, 4906, 4908, 4909, 4915, 4916, 4917, 4918, 4919, 4920, 4921, 4924; .claude/skills/sdlc-studio/scripts/tests/test_retro.py: 3826, 3827, 3828, 3829, 3834, 3835, 3836, 3837, 3838; .claude/skills/sdlc-studio/scripts/sprint.py: 5809, 5844, 5853; .claude/skills/sdlc-studio/scripts/tests/test_sprint.py: 6459, 20417, 20418, 20419, 20420, 20421, 20422, 20423, 20424, 20429, 20430, 20431, 20432, 20433, 20434, 20435, 20436, 20437. Rule a line equivalent with `verify_ac.py coverage rule --id BG0730 --file <path> --line <n> --reason <why>`, or reach it with a test
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Verification depth:** functional
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claim 23, still true and the most consequential survivor. `retro.carried_issues` parses the retro's table and never reads the named artefact's current status; `sprint_report.py:2144` collects every row whose ruling is `STOP_SHIP`; the checklist then returns non-zero while any `stop_ship` row stands. Nothing joins the ruling to the finding. So once a finding is ruled stop-ship it blocks every subsequent close FOREVER, including after it has been Fixed - the ruling outlives the thing it ruled on, and the only escape is editing a retro by hand.

## Steps to Reproduce

1. Rule a finding stop-ship in a retro's carried table. 2. Fix that finding and transition it to Fixed. 3. Run the close checklist on a later run. 4. The stop-ship row still stands and the checklist still refuses.

## Proposed Fix

Join each carried stop-ship row to its artefact's current status when the checklist is derived. A finding that has reached a terminal status is discharged - or, if the distinction matters, reported as `ruling outlived its finding` so a reader can see what happened - rather than counted as an unconditional blocker. Pin both: a stop-ship on an open finding still blocks, and the same row on a Fixed finding does not.

## Acceptance Criteria

### AC1: a stop-ship ruling on a finding that has reached a terminal status no longer blocks the close

- **Given** a retro carrying a stop-ship ruling on a finding that has since been Fixed, and a second ruling on a finding still Open as the control
- **When** the close checklist is derived
- **Then** the Open one still blocks and the Fixed one is discharged - or reported as a ruling that outlived its finding - so a ruling cannot outlive the thing it ruled on
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, collect every stop-ship row without joining it to its artefact's status, which is the shipped behaviour: a ruling then blocks every subsequent close forever and the only escape is editing a retro by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StopShipDischargeTests::test_a_ruling_on_a_fixed_finding_is_discharged_and_an_open_one_still_blocks
- **Verified:** yes (2026-09-22)

- [ ] **AC2: `retro.carried_issues` reports each carried row's CURRENT artefact status.**
  - **Given** a retro table naming a finding that has since reached a terminal status
  - **When** `carried_issues` parses it
  - **Then** each row carries the status read from the artefact, not only the text the table was written with - the parse never opened the artefact, which is why the join had nothing to join on
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::CarriedIssueStatusTests::test_a_carried_row_carries_its_artefact_s_current_status
  - **Verified:** yes (2026-09-22)
- [ ] **AC3: a carried row naming an artefact that cannot be read is reported, not discharged.**
  - **Given** a retro row naming an id with no file on disk
  - **When** the checklist is derived
  - **Then** it is reported as unreadable and still blocks - an unresolvable id is the one case where silently discharging would turn a typo into a released hold
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StopShipDischargeTests::test_an_unreadable_artefact_is_reported_and_still_blocks
  - **Verified:** yes (2026-09-22)

- [ ] **AC4: the printed row applies the same join as the gate, and the wiring exists.**
  - **Given** a real workspace whose retro carries a stop-ship ruling on a Fixed finding and one on an Open finding
  - **When** the checklist is derived through `_carried_issues`
  - **Then** the row reads `1 STOP-SHIP, 1 discharged` and names the discharged id - both halves had their own test and the single `root=root` joining them was pinned by nothing, so deleting it left every test green while the whole repair went inert
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StopShipDischargeTests::test_the_wiring_exists_end_to_end_on_a_real_workspace
  - **Verified:** yes (2026-09-22)
- [ ] **AC5: the close's SECOND reader discharges too.**
  - **Given** a batch holding a Fixed unit ruled stop-ship
  - **When** `sprint.unanswered_units` runs
  - **Then** the unit is not held - the checklist discharging while `unanswered_units` refused meant the close still blocked on the Fixed finding, which is this bug's summary sentence verbatim
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StopShipDischargeInUnansweredUnitsTests::test_a_discharged_ruling_no_longer_holds_its_unit
  - **Verified:** yes (2026-09-22)
- [ ] **AC6: an id of any admitted type resolves.**
  - **Given** carried rows naming a US, an RFC and an EP, each with a readable file
  - **When** the rows are parsed with a root
  - **Then** none is marked unreadable - the row grammar admits CR, BG, US, RFC, EP and LL, and guessing the type from the prefix asserted `no file resolves` about four of the six while their files sat there readable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StopShipDischargeTests::test_an_id_of_any_admitted_type_resolves
  - **Verified:** yes (2026-09-22)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint_report.py`, collect every stop-ship row without joining it to its artefact's status - the shipped behaviour | a Fixed ruling is discharged, an Open one blocks |
| AC2 | in `retro.py`, return each carried row from the table text alone, without reading the artefact it names | a carried row carries its current status |
| AC3 | in `sprint_report.py`, treat an unreadable artefact as terminal so its ruling discharges | an unreadable artefact still blocks |
| AC4 | in `sprint_report.py`, stop passing the root through `_carried_issues`, so every row comes back unjoined and the repair is inert | the wiring exists |
| AC4 | in `sprint_report.py`, let the printed row count every stop-ship ruling while the gate discharges some | the row matches the gate |
| AC5 | in `sprint.py`, hold a unit on a discharged ruling, so the close still refuses on a Fixed finding | the second reader discharges |
| AC6 | in `retro.py`, guess the artefact type from the id prefix instead of resolving it, marking readable US, RFC and EP files unreadable | any admitted id resolves |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | Claude Opus 5 | Round 2 - the review REJECTed on four blocking findings and the sharpest was that the single line joining the two halves was pinned by nothing: deleting `root=root` left every test green while the repair went inert, which is this repository's own recorded scar. It also found the printed checklist row still counting every stop-ship ruling while the gate discharged some, so the operator read `2 STOP-SHIP` beside a close that proceeded past one; a type guess that marked readable US, RFC and EP files UNREADABLE, the opposite of what that flag asserts, where `sdlc_md.find_by_id` was the shipped lookup all along; and `sprint.unanswered_units` still refusing on the Fixed finding, so end to end the bug was unfixed. `Affects` widens to `sprint.py`, because the unit cannot be delivered without its second reader. Points 3 to 5. |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-22 | transition set --force | forced BG0730 -> Fixed, waiving 1 gate(s): BG0730: 253 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2043, 2046, 2093, 2094, 2109, 2114, 2115, 2130, 2131, 2132, 2133, 2134, 2135, 2136, 2137, 2142, 2143, 2144, 2145, 2146, 2147, 2148, 2149, 2182, 2188, 2189, 2190, 2197, 2203, 2205, 2504, 2505, 2509, 2510, 3426, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3768, 3769, 3770, 3771, 3775, 3780, 3787, 3788, 3792, 3797, 3798, 3801, 3804, 3809; .claude/skills/sdlc-studio/scripts/retro.py: 335; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4479, 4480, 4481, 4482, 4490, 4495, 4496, 4497, 4498, 4503, 4504, 4505, 4513, 4514, 4515, 4516, 4517, 4518, 4520, 4522, 4526, 4528, 4529, 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4550, 4551, 4555, 4557, 4558, 4559, 4565, 4566, 4567, 4572, 4573, 4574, 4575, 4582, 4583, 4584, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4632, 4633, 4634, 4635, 4636, 4637, 4733, 4736, 4737, 4749, 4750, 4751, 4753, 4754, 4758, 4760, 4761, 4762, 4763, 4764, 4765, 4771, 4775, 4780, 4781, 4782, 4790, 4792, 4793, 4800, 4801, 4802, 4803, 4804, 4805, 4807, 4813, 4814, 4815, 4816, 4817, 4819, 4820, 4825, 4826, 4834, 4836, 4840, 4841, 4843, 4844, 4845, 4848, 4849, 4850, 4852, 4854, 4855, 4856, 4857, 4865, 4866, 4869, 4870, 4872, 4873, 4874, 4877, 4878, 4879, 4880, 4881, 4882, 4887, 4894, 4895, 4902, 4904, 4905, 4906, 4908, 4909, 4915, 4916, 4917, 4918, 4919, 4920, 4921, 4924; .claude/skills/sdlc-studio/scripts/tests/test_retro.py: 3826, 3827, 3828, 3829, 3834, 3835, 3836, 3837, 3838; .claude/skills/sdlc-studio/scripts/sprint.py: 5809, 5844, 5853; .claude/skills/sdlc-studio/scripts/tests/test_sprint.py: 6459, 20417, 20418, 20419, 20420, 20421, 20422, 20423, 20424, 20429, 20430, 20431, 20432, 20433, 20434, 20435, 20436, 20437. Rule a line equivalent with `verify_ac.py coverage rule --id BG0730 --file <path> --line <n> --reason <why>`, or reach it with a test |
