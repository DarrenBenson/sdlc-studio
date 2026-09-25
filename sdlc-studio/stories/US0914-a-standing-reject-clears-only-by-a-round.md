# US0914: A standing REJECT clears only by a round-2 APPROVE or by carrying the unit

> **Status:** Draft
> **Depends on:** US0911, US0915 - plan_review_repair_clears and repair --phase (EP0263 readiness)
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py, changelog.d/US0914.md
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
- **AC4:** Given a standing REJECT from one reviewer and a later APPROVE from a different reviewer whose `--brief` fingerprint matches the REJECT's, both recorded after the same-reviewer round rule (`round_refusal`) shipped, when `_unanswered_rejects` runs, then the REJECT stands unanswered; a historical pair recorded before that rule still matches by fingerprint, so the 19 historical units stay answered. Fails on: HEAD's unscoped fingerprint second key (critic.py 867-870), which lets an invented `--brief` retire a REJECT once US0923 stops marking unmatched briefs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_fingerprint_key_answers_only_historic_rows
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py repair` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given the criteria whose stamped Verify selector names a test this story deletes (ClosureChannelTests, RepairRecordTests, ClosureResolutionTests, ClosureArrowTests, PartialRepairTests, FiledDispositionTests, LedgerRollupTests, RepairPlacementTests, RepairPhaseJoinTests less its plan-review test, and RepairStateResolvesFiledIdsTests): BG0604 (1), BG0605 (2), BG0607 (5), BG0611 (2), BG0618 (8), BG0629 (2), BG0631 (4), BG0677 (7), BG0704 (3), US0620 (4), US0622 (3), US0623 (3) and US0627 (2), then each is retired in the D0259 pattern (`Verify: manual - retired by US0914: <why>`, `Verified: manual (<date>) - retired, superseded by US0914`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node. `RejectNeedsAnAnswerTests` and `ClosedOverRejectNamesTheBugTests` are edited, not deleted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- Deletes about 750 lines of `critic.py`: `record_repair`, the closures, `resolve_finding`, `repairs_for`, `repair_state`, `plan_review_repair_clears`, `cmd_repair` and its parser. Readers go from `transition.py` (1028-1080, 1518-1535), `conformance.py:404`, `sprint.py` (1593, 5323, 5398, 5675-5746) and `sprint_report.py` (1264, 1951, 2563). `test_lean_review_cap.py` calls `critic.repairs_for`.
- The old AC3 (the two exits still work) passed at HEAD, so it is now the control half of AC2.
- AC4 is the design hole the readiness review named. It narrows an existing licence rather than adding a check, so the ratchet rule is not engaged. Engineering call: scope the key by the row's recorded date against the date `round_refusal` shipped, held as one named constant.
- Stamps: 13 units measured by selector. The readiness estimate was 18; AC6's no-deleted-node clause catches any selector the enumeration missed. US0314 retires with US0913. BG0631's plan-review test in RepairPhaseJoinTests retires with US0915.
- Lands after US0911 and US0915, and before US0923.
- The shared prose edit to `reference-scripts-review.md` moved to US0924.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 5 -> 8 points; the old AC3 exits folded into AC2 as its control; the ledger criterion (now AC3) uses a fixture whose closure rows change HEAD's output; new AC4 scopes the fingerprint second key to historic rows before US0923; stamps measured and named (13 units, 46 criteria); Affects adds test_lean_review_cap.py and the changelog fragment, and moves reference-scripts-review.md to US0924 |
