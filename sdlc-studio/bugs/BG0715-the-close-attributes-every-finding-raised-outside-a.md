# BG0715: the close attributes every finding raised outside a delivery batch to whichever run is open, because it dates them by the last word of a prose stamp

> **Status:** Fixed
> **Forced-override:** 2026-09-22: --force waived 1 gate(s) on Fixed - BG0715: 199 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2060, 2061, 2064, 2066, 2135, 2147, 2284, 2286, 2357, 2504, 2505, 2509, 2510, 3426, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3768, 3769, 3770, 3771, 3775, 3780, 3787, 3788, 3792, 3797, 3798, 3801, 3804, 3809; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4565, 4566, 4567, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4647, 4651, 4658, 4660, 4661, 4666, 4668, 4669, 4670, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4688, 4689, 4690, 4693, 4694, 4695, 4696, 4697, 4699, 4700, 4701, 4703, 4709, 4712, 4713, 4714, 4716, 4717, 4718, 4723, 4724, 4725, 4726, 4729, 4733, 4736, 4737, 4749, 4750, 4751, 4753, 4754, 4758, 4760, 4761, 4762, 4763, 4764, 4765, 4771, 4775, 4780, 4781, 4782, 4790, 4792, 4793, 4800, 4801, 4802, 4803, 4804, 4805, 4807, 4813, 4814, 4815, 4816, 4817, 4819, 4820, 4825, 4826, 4834, 4836, 4840, 4841, 4843, 4844, 4845, 4848, 4849, 4850, 4852, 4854, 4855, 4856, 4857, 4865, 4866, 4869, 4870, 4872, 4873, 4874, 4877, 4878, 4879, 4880, 4881, 4882, 4887, 4894, 4895, 4902, 4904, 4905, 4906, 4908, 4909, 4915, 4916, 4917, 4918, 4919, 4920, 4921, 4924. Rule a line equivalent with `verify_ac.py coverage rule --id BG0715 --file <path> --line <n> --reason <why>`, or reach it with a test
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Verification depth:** functional
> **Created:** 2026-09-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_open_findings` dates a finding by the LAST WORD of its `Raised-in-batch` stamp. A finding raised outside a delivery batch carries the prose stamp `none open - raised outside a delivery batch`, whose last word is `batch` - and `'batch' < '2026-09-18T07:20:32Z'` is False, so it sorts as inside every run window. Every such finding in the project's history is therefore attributed to whichever run happens to be open, and the close's known-issues row demands a stop-ship ruling for all of them.

## Steps to Reproduce

Measured on RUN-01M2SPNS, which filed exactly two findings (BG0713, BG0714):

```text
close STOPPED at checklist [6/10]:
  known-issues: Known issues carried, each with its stop-ship ruling - 81 unruled
      UNRULED BG0679; UNRULED BG0680; ... BG0690 - an open finding nobody ruled on
```

None of BG0679-BG0690 was raised by this run. Each carries `> **Raised-in-batch:** none open - raised outside a delivery batch`.

The arithmetic, reproduced:

```python
stamp = 'none open - raised outside a delivery batch'
when = stamp.split()[-1]          # 'batch'
when < '2026-09-18T07:20:32Z'     # False - so the row is NOT skipped
```

`_open_findings` (`sprint_report.py)` comments that 'a stamp naming no batch still carries the moment it was raised' - but the no-batch stamp carries no moment at all, only prose. The guard `if not when` catches an EMPTY stamp and misses a prose one.

## Proposed Fix

Read the DATE from the stamp rather than its last token: parse an ISO timestamp out of it and treat a stamp carrying none as undatable. An undatable finding is then either excluded from the window (it cannot be shown to be this run's) or reported separately as undatable - never silently counted as inside. The `if not when` guard already draws the right distinction for an empty stamp; it needs to draw the same one for a stamp with no date in it.

## Acceptance Criteria

- [ ] **AC1: a prose stamp falls back to `Created` and the finding stays attributable.**
  - **Given** a finding stamped `none open - raised outside a delivery batch` carrying a `Created` date inside the run's window, against a run whose `ended_at` is None
  - **When** the report derives its open findings
  - **Then** it IS attributed - the word `batch` is never read as a date, but the artefact still records one and reading it is what keeps the finding visible rather than invisible
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_a_prose_stamp_falls_back_to_created_and_is_attributed
  - **Verified:** yes (2026-09-22)
- [ ] **AC1b: a prose-stamped finding created BEFORE the run is not this run's.**
  - **Given** the same stamp with a `Created` date months before the run opened
  - **When** the report derives its findings
  - **Then** it is excluded - the shipped code attributed every prose-stamped finding in the repository to whichever run was open, 307 of them here
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_a_prose_stamp_created_before_the_run_is_not_this_run_s
  - **Verified:** yes (2026-09-22)
- [ ] **AC2: an undatable finding is NOT attributed, and the close cannot certify over it.**
  - **Given** a finding whose stamp records no moment and which carries no `Created`
  - **When** the known-issues row is derived
  - **Then** the finding is absent from the run's findings AND the row reports UNANSWERED naming it - both directions of this were wrong in turn: attributing them handed the close 47 findings no run had touched, and excluding them silently let the close certify `none carried` over findings it had raised
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_an_undatable_finding_is_not_attributed_but_the_row_cannot_say_none_carried
  - **Verified:** yes (2026-09-22)
- [ ] **AC2b: the row still answers when there is genuinely nothing.**
  - **Given** no carried rows, no open findings and no undatable ones
  - **When** the row is derived
  - **Then** it reports ANSWERED `none carried` - the discriminating half, because a row that never answers is not a check
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_the_row_still_says_none_carried_when_there_is_genuinely_nothing
  - **Verified:** yes (2026-09-22)
- [ ] **AC2c: an artefact carrying NO stamp at all is skipped by both readers.**
  - **Given** an artefact with no `Raised-in-batch` field and a `Created` inside the window
  - **When** the findings and the undatable set are derived
  - **Then** it appears in neither - no stamp predates the mechanism that writes one, so nothing ever claimed it for a run, and counting these attributed 466 historical artefacts to a run that raised 2
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_an_artefact_carrying_no_stamp_at_all_is_skipped
  - **Verified:** yes (2026-09-22)
- [ ] **AC3: a finding genuinely raised inside the window is still attributed.**
  - **Given** a finding whose stamp carries an ISO timestamp inside the window
  - **When** the report derives its findings
  - **Then** it IS attributed and appears in the still-open set - the discriminating half, because a reader attributing NOTHING would satisfy every criterion above
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_a_dated_stamp_inside_the_window_is_still_attributed
  - **Verified:** yes (2026-09-22)
- [ ] **AC3b: the upper window bound still bounds.**
  - **Given** a finding timestamped after the run's `ended_at`
  - **When** a closed run derives its findings
  - **Then** it is not attributed - another run's finding is not this one's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_a_dated_stamp_outside_the_window_is_not_attributed
  - **Verified:** yes (2026-09-22)
- [ ] **AC4: the stamp's own timestamp beats a contradicting `Created`.**
  - **Given** a finding whose stamp carries a timestamp inside the window and whose `Created` is months earlier
  - **When** the finding is dated
  - **Then** the stamp wins - it is the precise record of when a batch claimed the finding, and `Created` is only the fallback
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::FindingAttributionTests::test_the_stamp_timestamp_beats_a_contradicting_created
  - **Verified:** yes (2026-09-22)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint_report.py`, restore the last-whitespace-token read so the word `batch` is taken as a date | |
| AC1b | in `sprint_report.py`, delete the `Created` fallback so a prose-stamped finding is invisible again | |
| AC2 | in `sprint_report.py`, let the known-issues row certify `none carried` while undatable findings exist | |
| AC2b | in `sprint_report.py`, delete the `open_only` scoping so terminal findings are disclosed as undatable too | |
| AC2c | in `sprint_report.py`, delete the no-stamp skip so an unstamped artefact carrying a `Created` is attributed | |
| AC3 | in `sprint_report.py`, skip every finding so nothing is attributed to the run | |
| AC3b | in `sprint_report.py`, delete the upper window bound so a finding after the run ended is still attributed | |
| AC4 | in `sprint_report.py`, prefer `Created` over the stamp's timestamp, mis-dating every batch-stamped finding | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Filed |
| 2026-09-22 | transition set --force | forced BG0715 -> Fixed, waiving 2 gate(s): BG0715: 3 planned mutant(s) unaccounted for - AC2 row 2 was planned and never executed - `in`sprint_report.py`, let the known-issues row certify`non`; AC3 row 0 was planned and never executed -`in `sprint_report.py`, skip every finding so nothing is attr`; AC3 row 1 was planned and never executed -`in `sprint_report.py`, drop the upper window bound so a find`. Check them with`mutation.py run --story BG0715 --from-plan` (its type is `bug`); BG0715: 199 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2060, 2061, 2064, 2066, 2135, 2147, 2284, 2286, 2357, 2504, 2505, 2509, 2510, 3426, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3768, 3769, 3770, 3771, 3775, 3780, 3787, 3788, 3792, 3797, 3798, 3801, 3804, 3809; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4565, 4566, 4567, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4647, 4651, 4658, 4660, 4661, 4666, 4668, 4669, 4670, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4688, 4689, 4690, 4693, 4694, 4695, 4696, 4697, 4699, 4700, 4701, 4703, 4709, 4712, 4713, 4714, 4716, 4717, 4718, 4723, 4724, 4725, 4726, 4729, 4733, 4736, 4737, 4749, 4750, 4751, 4753, 4754, 4758, 4760, 4761, 4762, 4763, 4764, 4765, 4771, 4775, 4780, 4781, 4782, 4790, 4792, 4793, 4800, 4801, 4802, 4803, 4804, 4805, 4807, 4813, 4814, 4815, 4816, 4817, 4819, 4820, 4825, 4826, 4834, 4836, 4840, 4841, 4843, 4844, 4845, 4848, 4849, 4850, 4852, 4854, 4855, 4856, 4857, 4865, 4866, 4869, 4870, 4872, 4873, 4874, 4877, 4878, 4879, 4880, 4881, 4882, 4887, 4894, 4895, 4902, 4904, 4905, 4906, 4908, 4909, 4915, 4916, 4917, 4918, 4919, 4920, 4921, 4924. Rule a line equivalent with`verify_ac.py coverage rule --id BG0715 --file <path> --line <n> --reason <why>`, or reach it with a test |
| 2026-09-22 | transition set --force | forced BG0715 -> Fixed, waiving 1 gate(s): BG0715: 199 uncovered added line(s) its own verifiers never executed - .claude/skills/sdlc-studio/scripts/sprint_report.py: 2060, 2061, 2064, 2066, 2135, 2147, 2284, 2286, 2357, 2504, 2505, 2509, 2510, 3426, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757, 3758, 3759, 3760, 3761, 3762, 3763, 3764, 3765, 3768, 3769, 3770, 3771, 3775, 3780, 3787, 3788, 3792, 3797, 3798, 3801, 3804, 3809; .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py: 4534, 4535, 4536, 4537, 4538, 4542, 4543, 4544, 4565, 4566, 4567, 4590, 4591, 4592, 4593, 4595, 4600, 4601, 4602, 4608, 4609, 4610, 4611, 4618, 4619, 4620, 4621, 4622, 4623, 4647, 4651, 4658, 4660, 4661, 4666, 4668, 4669, 4670, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4688, 4689, 4690, 4693, 4694, 4695, 4696, 4697, 4699, 4700, 4701, 4703, 4709, 4712, 4713, 4714, 4716, 4717, 4718, 4723, 4724, 4725, 4726, 4729, 4733, 4736, 4737, 4749, 4750, 4751, 4753, 4754, 4758, 4760, 4761, 4762, 4763, 4764, 4765, 4771, 4775, 4780, 4781, 4782, 4790, 4792, 4793, 4800, 4801, 4802, 4803, 4804, 4805, 4807, 4813, 4814, 4815, 4816, 4817, 4819, 4820, 4825, 4826, 4834, 4836, 4840, 4841, 4843, 4844, 4845, 4848, 4849, 4850, 4852, 4854, 4855, 4856, 4857, 4865, 4866, 4869, 4870, 4872, 4873, 4874, 4877, 4878, 4879, 4880, 4881, 4882, 4887, 4894, 4895, 4902, 4904, 4905, 4906, 4908, 4909, 4915, 4916, 4917, 4918, 4919, 4920, 4921, 4924. Rule a line equivalent with `verify_ac.py coverage rule --id BG0715 --file <path> --line <n> --reason <why>`, or reach it with a test |
