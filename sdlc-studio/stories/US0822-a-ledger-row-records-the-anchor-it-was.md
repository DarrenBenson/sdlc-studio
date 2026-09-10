# US0822: A ledger row records the anchor it was applied to, and staleness is judged from it

> **Status:** Ready
> **Delivers:** CR0570
> **Created:** 2026-09-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0252
> **Points:** 11
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A ledger row records the anchor it was applied to, and staleness is judged from it
**So that** CR0570 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a row registered WITH an anchor, when an unrelated line elsewhere in the same target is edited, then the row stays LIVE and the evidence-drift lane does not demand it be re-measured. Measured on the live ledger: 26 of 74 targets carry rows from more than one unit and `verify_ac.py` carries seven units' worth, so an edit anywhere in it currently re-measures all seven
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AnchoredStalenessTests::test_an_unrelated_edit_leaves_an_anchored_row_live
  - **Verified:** no
- [ ] **AC2** Given the same row, when the text its anchor names is edited, then it is STALE, and the lane names that ROW rather than the whole file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AnchoredStalenessTests::test_editing_the_anchored_text_stales_that_row
  - **Verified:** no
- [ ] **AC3** Given a row whose anchor now occurs MORE THAN ONCE in the target, then it is STALE as well. An anchor that no longer identifies one site cannot say which site the verdict was about, and reading it as live reports a measurement nobody made - the same reasoning that makes `register` refuse a non-unique anchor today
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AnchoredStalenessTests::test_an_anchor_matching_twice_is_stale_not_live
  - **Verified:** no
- [ ] **AC4** Given a row registered with NO anchor - which is all 515 rows on disk today - then it is judged by the target's content hash exactly as it is now. A widening that silently promoted the unanchored rows to live would turn a cost into a correctness failure, and this repository has already shipped a schema widened without testing its oldest shape
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AnchoredStalenessTests::test_a_row_with_no_anchor_is_still_judged_by_the_file_hash
  - **Verified:** no
- [ ] **AC5** Given `mutation.py register --anchor`, when the row is written, then the anchor is PERSISTED on it; and an anchor occurring other than exactly once is still refused at registration. The value is validated today and then discarded, which is why nothing on a row can answer whether its own site moved
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AnchoredStalenessTests::test_register_persists_the_anchor_and_still_refuses_a_non_unique_one
  - **Verified:** no
- [ ] **AC6** Given a target holding rows from several units and an edit touching one unit's site, when the evidence-drift lane runs through the shipped gate, then it names only the rows whose anchors moved and does not demand the others be re-measured. The library answer is not the one a committer meets; the lane is
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::AnchoredDriftLaneTests::test_the_lane_names_only_the_rows_whose_anchors_moved
  - **Verified:** no

- [ ] **AC7** Given `mutation.py register` invoked for a self-reported row with no `--anchor`, when it runs, then it REFUSES, naming the flag and what to pass - the text the mutant replaced, quoted until it is unique. Without this the unit's saving stays notional: 515 of 515 live rows carry no anchor today, AC4 keeps every one of them on the file hash, and nothing converts them. Requiring it at the write is the honest migration - a row gains its anchor at the moment somebody actually measures it, rather than by a backfill inventing an anchor for a measurement nobody re-ran
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AnchorIsRequiredTests::test_a_self_reported_registration_without_an_anchor_is_refused
- [ ] **AC8** Given each printed remedy that tells a reader to run `mutation.py register`, when that remedy is run as printed, then it is accepted rather than refused for the flag AC7 now demands. Three sites print one today and none names the flag, so making it required would ship a tool whose own instructions no longer work. Judged by RUNNING the printed string, not by reading the source that composes it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AnchorIsRequiredTests::test_every_printed_register_remedy_runs_as_printed

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/mutation.py, ignore the stored anchor and fall back to the entry's content hash for every row | Given a row registered WITH an anchor, when an unrelated line elsewhere in the same target is edited, then the row stays LIVE and the evidence-drift lane does not demand it be re-measured. Measured on the live ledger: 26 of 74 targets carry rows from more than one unit and `verify_ac.py` carries seven units' worth, so an edit anywhere in it currently re-measures all seven |
| AC2 | in .claude/skills/sdlc-studio/scripts/mutation.py, invert the zero-occurrence branch so it returns live | Given the same row, when the text its anchor names is edited, then it is STALE, and the lane names that ROW rather than the whole file |
| AC3 | in .claude/skills/sdlc-studio/scripts/mutation.py, replace the equality test on the occurrence count with a greater-than-zero test | Given a row whose anchor now occurs MORE THAN ONCE in the target, then it is STALE as well. An anchor that no longer identifies one site cannot say which site the verdict was about, and reading it as live reports a measurement nobody made - the same reasoning that makes `register` refuse a non-unique anchor today |
| AC4 | in .claude/skills/sdlc-studio/scripts/mutation.py, skip the hash comparison when the field is absent | Given a row registered with NO anchor - which is all 515 rows on disk today - then it is judged by the target's content hash exactly as it is now. A widening that silently promoted the unanchored rows to live would turn a cost into a correctness failure, and this repository has already shipped a schema widened without testing its oldest shape |
| AC5 | in .claude/skills/sdlc-studio/scripts/mutation.py, omit the field from the dict `register_mutant` builds | Given `mutation.py register --anchor`, when the row is written, then the anchor is PERSISTED on it; and an anchor occurring other than exactly once is still refused at registration. The value is validated today and then discarded, which is why nothing on a row can answer whether its own site moved |
| AC5 | in .claude/skills/sdlc-studio/scripts/mutation.py, remove the uniqueness test applied to the anchor at registration | Given `mutation.py register --anchor`, when the row is written, then the anchor is PERSISTED on it; and an anchor occurring other than exactly once is still refused at registration. The value is validated today and then discarded, which is why nothing on a row can answer whether its own site moved |
| AC6 | in .claude/skills/sdlc-studio/scripts/gate.py, report the whole entry when any row on a target moved, rather than the moved rows | Given a target holding rows from several units and an edit touching one unit's site, when the evidence-drift lane runs through the shipped gate, then it names only the rows whose anchors moved and does not demand the others be re-measured. The library answer is not the one a committer meets; the lane is |

| AC7 | in .claude/skills/sdlc-studio/scripts/mutation.py, delete the refusal for a missing anchor so the write falls through | Given mutation.py register invoked for a self-reported row with no anchor flag, when it runs, then it REFUSES, naming the flag and what to pass |
| AC8 | in .claude/skills/sdlc-studio/scripts/transition.py, drop the anchor argument from the remedy the Fixed gate prints | Given each printed remedy that tells a reader to run mutation.py register, when that remedy is run as printed, then it is accepted rather than refused for the flag AC7 demands |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-10 | Claude Opus 5 | Regroomed 8 -> 11 points with a MIGRATION half, on the operator's ruling after a plan reviewer refuted the unit's premise: AC1 to AC6 give an anchored row the benefit, AC4 keeps every unanchored row on the file hash, and all 515 live rows are unanchored - so as groomed the unit bought nothing in the run that built it. AC7 requires the anchor at registration and AC8 pins the three printed remedies that would otherwise tell a reader to run a command the tool now refuses. Backfill was considered and rejected: deriving an anchor for a row nobody re-measured asserts a site for a measurement that was never taken there, which is the class of evidence this project refused once already |
