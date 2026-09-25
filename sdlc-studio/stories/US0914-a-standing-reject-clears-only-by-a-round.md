# US0914: A standing REJECT clears only by a round-2 APPROVE or by carrying the unit

> **Status:** Draft
> **Depends on:** US0937 (US0891, US0900 and US0904 reach Done first)
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py, changelog.d/US0914.md
> **Epic:** EP0263
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer answering a review
**I want** a REJECT to have exactly two exits, a round-2 APPROVE from the reviewer who rejected or carrying the unit as a known issue at the cap
**So that** no unit is argued through a repair ledger's closures, and every rejected unit ends either approved or visibly carried

## Acceptance Criteria

- **AC1:** Given `critic.py repair`, when invoked, then it exits 2 with a message that it is retired naming the two exits (a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the review cap), and `critic.py --help` does not list it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_repair_verb_is_retired
- **AC2:** Given a fixture unit whose standing delivery REJECT has every finding closed by a row in a pre-existing `repair-record.md`, when it is moved to Done, then it is refused as an unanswered REJECT and the refusal names the two exits, not `critic.py repair`; the same REJECT answered by a round-2 independent APPROVE from the rejecting reviewer reaches Done with critiqued met, and a round-2 REJECT instead carries the unit (dropped from the batch with a filed bug). Fails on: HEAD, where the closure rows answer the REJECT, and on a deletion that also breaks either exit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_a_repair_row_no_longer_answers_a_reject
- **AC3:** Given a fixture unit whose standing delivery REJECT has every finding closed by rows in `repair-record.md`, when conformance, the close and the sprint report run, then each output is identical with the file removed, and its bytes are unchanged. Fails on: removing the Done-side read while `sprint.py` or `sprint_report.py` still counts closures
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_repair_ledger_is_frozen_and_unread
- **AC4:** Given a standing REJECT from one reviewer and a later APPROVE from a different reviewer whose `--brief` fingerprint matches the REJECT's, both recorded after the same-reviewer round rule (`round_refusal`) shipped, when `_unanswered_rejects` runs, then the REJECT stands unanswered; a historical pair recorded before that rule still matches by fingerprint, so the 23 historical units it pairs in this repository stay answered. Fails on: HEAD's unscoped fingerprint second key (critic.py 867-870), which lets an invented `--brief` retire a REJECT once US0923 stops marking unmatched briefs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_fingerprint_key_answers_only_historic_rows
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py repair` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given the criteria whose stamped Verify selector names a test this story deletes (ClosureChannelTests and LedgerRollupTests less the eight tests that pin surviving behaviour, RepairRecordTests, ClosureResolutionTests, ClosureArrowTests, PartialRepairTests, FiledDispositionTests, RepairPlacementTests, RepairPhaseJoinTests and RepairStateResolvesFiledIdsTests), measured from the built retire patch: BG0605 (2), BG0607 (2), BG0618 (6), BG0629 (2), BG0631 (4), BG0637 (1), BG0677 (7), BG0704 (3), US0620 (4), US0621 (3), US0622 (3), US0623 (3), US0624 (1), US0627 (6) and US0628 (4), 51 criteria, then each is retired in the D0259 pattern (`Verify: manual - retired by US0914: <why>`, `Verified: manual (<date>) - retired, superseded by US0914`), US0626 AC4/AC5 and US0628 AC5/AC6 are narrowed to what survives, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node. `RejectNeedsAnAnswerTests` and `ClosedOverRejectNamesTheBugTests` are edited, not deleted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_no_stamp_names_a_deleted_test
- **AC7:** Given a fixture story at Done whose standing delivery REJECT is dated before `critic.REPAIR_VERB_RETIRED` (the day this story lands, after the last repair row of 2026-09-25), with no round-2 APPROVE and no `repair-record.md`, when `conformance.py check` runs, then critiqued is met and the summary counts the story as passed on the repair-ledger licence; the same story with its REJECT dated on the constant reads `missing critiqued`; and an In Progress copy of the pre-constant story moved to Done by `transition.py set` is still refused as an unanswered REJECT. Fails on: no licence (in this repository 38 Done stories answered only by repair rows lose critiqued, 854 to 814 of 936, measured on HEAD plus the built patch); a licence with no date (the on-constant REJECT reads met); the licence placed in `critic._unanswered_rejects` or the transition guard (the In Progress copy reaches Done unanswered)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_a_unit_done_under_the_frozen_ledger_stays_critiqued

## Notes

- Deletes about 750 lines of `critic.py`: `record_repair`, the closures, `resolve_finding`, `repairs_for`, `repair_state`, `plan_review_repair_clears`, `cmd_repair` and its parser. Readers go from `transition.py` (1028-1080, 1518-1535), `conformance.py:404`, `sprint.py` (1593, 5323, 5398, 5675-5746) and `sprint_report.py` (1264, 1951, 2563). `test_lean_review_cap.py` calls `critic.repairs_for`.
- The old AC3 (the two exits still work) passed at HEAD, so it is now the control half of AC2.
- AC4 is the design hole the readiness review named. It narrows an existing licence rather than adding a check, so the ratchet rule is not engaged. Engineering call: scope the key by the row's recorded date against the date `round_refusal` shipped, held as one named constant.
- Stamps: 13 units measured by selector. The readiness estimate was 18; AC6's no-deleted-node clause catches any selector the enumeration missed. US0314 retires with US0913. BG0631's plan-review test in RepairPhaseJoinTests retires with US0915.
- Lands after US0911 and US0915, and before US0923.
- The shared prose edit to `reference-scripts-review.md` moved to US0924.
- - D0269's historical answer, measured at 013a46d0: 173 terminal units carry a standing delivery REJECT (97 answered only by a complete repair, 70 by none, 6 partial); conformance judges stories, and of those 38 Done stories are answered only by repair rows, every other one waived or exempt. The 38 REJECTs are dated 2026-07-31 to 2026-09-25, so `ROUND_RULE_SHIPPED` (2026-09-23) is too early for this licence: US0905 (09-24), US0909 and US0915 (09-25) fall after it.
- AC7's licence reads no ledger: it keys on the REJECT row's own date against one named constant and lives only in `conformance.verdict_half_ok`, the reader of history. The Done guard, the close and the sprint report stay unlicensed. Simulated on a copy with the constant at 2026-09-26: whole-workspace conformance returns to 854/936, 0 not. US0918 reuses the same constant for the frozen batch-review read.
- The builder quotes whole-workspace `conformance.py check` before and after in the hand-back. That is review evidence, not a pinned live-repo count (LC-008, D0271).
- The built patch (`sdlc-studio/.local/US0914-built.patch` and `-retire.patch`) applies to 013a46d0 except `reference-scripts-surface.md`, which is derived and regenerated. On HEAD plus the patch the full skill suite is green under `unittest discover` (6,889 tests).
- Lands after NEW-A (US0891, US0900 and US0904 each carry a 2026-09-24 REJECT answered only by a repair row) and before US0918 and US0923. Closes BG0680, BG0690 and BG0704 in the same commit (D0264).
- AC6's list is the build's measured one: BG0604 and BG0611 are not touched (their selectors name no deleted node), and BG0637, US0621 and US0624 are.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 5 -> 8 points; the old AC3 exits folded into AC2 as its control; the ledger criterion (now AC3) uses a fixture whose closure rows change HEAD's output; new AC4 scopes the fingerprint second key to historic rows before US0923; stamps measured and named (13 units, 46 criteria); Affects adds test_lean_review_cap.py and the changelog fragment, and moves reference-scripts-review.md to US0924 |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 grooming (engineering seat): AC7 adds D0269's date-scoped historical licence (`REPAIR_VERB_RETIRED`), measured at 38 stories; AC6's list replaced by the built retire patch's (51 criteria); AC4's historical count corrected to 23; Affects adds test_lean_no_plan_phase.py |
