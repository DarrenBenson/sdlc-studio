# US0918: One verdict ledger decides whether a unit was reviewed

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py, changelog.d/US0918.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, sdlc-studio/bugs/BG0441-review-coverage-launders-a-recorded-reject-into-coverage.md, sdlc-studio/bugs/BG0499-panel-escalation-reads-a-different-ledger-from-the.md, sdlc-studio/bugs/BG0659-a-code-span-whose-value-ends-in-a.md, sdlc-studio/stories/US0247-a-recorded-sprint-level-adversarial-full-diff-verdict.md, sdlc-studio/stories/US0261-count-review-rounds-on-the-run-state-and.md, sdlc-studio/stories/US0560-a-delivery-batch-reaching-the-commit-threshold-has.md, sdlc-studio/stories/US0561-a-batch-review-finding-is-filed-as-a.md, sdlc-studio/stories/US0562-sprint-close-refuses-a-batch-containing-units-no.md, sdlc-studio/stories/US0563-the-shipped-lifecycle-states-the-batch-boundary-cadence.md, sdlc-studio/stories/US0615-sprint-review-batch-takes-its-findings-from-a.md, .claude/skills/sdlc-studio/reference-scripts-review.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer checking what is really done
**I want** a unit to count as reviewed when its latest delivery verdict is an independent APPROVE, with the evidence and sprint-review ledgers no longer read
**So that** one ledger answers 'was this reviewed', so status cannot disagree with itself across four files

## Acceptance Criteria

- **AC1:** Given `critic.py evidence`, `critic.py sprint-review` or `sprint.py review-batch`, when invoked, then each exits 2 with a message that it is retired naming `critic.py record` for a per-unit delivery verdict, and neither script's `--help` lists them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_ledger_verbs_are_retired
  - **Verified:** yes (2026-09-26)
- **AC2:** Given a Done fixture story covered only by a `sprint-review-record.md` APPROVE row dated on or after `critic.REPAIR_VERB_RETIRED`, when `conformance.py check` runs, then critiqued is unmet naming the missing independent APPROVE; the same row dated before the constant covers the story; and an independent delivery APPROVE covers it either way. Fails on: HEAD, where the on-constant row covers; deleting the batch-review read outright, where the pre-constant row stops covering (in this repository 253 Done stories are covered only by such rows, and conformance falls from 854 to 670 of 936, measured by stubbing the read)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_only_a_frozen_batch_row_or_a_delivery_approve_covers
  - **Verified:** yes (2026-09-26)
- **AC3:** Given a Done unit with a `critic-evidence.md` row and a pre-constant `sprint-review-record.md` row, when conformance, the gate, the close and the sprint report run, then each output is identical with `critic-evidence.md` removed, both files' bytes are unchanged, and no shipped script calls `critic.evidence_for`. Fails on: removing conformance's read while `sprint.py` (5166, 5476, 6154) still reads evidence rows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_evidence_ledger_is_frozen_and_unread
  - **Verified:** yes (2026-09-26)
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py evidence`, `critic.py sprint-review` or `sprint.py review-batch` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_surface_names_no_retired_verb
  - **Verified:** yes (2026-09-26)
- **AC5:** Given the criteria whose stamped Verify selector names a test this story deletes (EvidenceTests, SprintReviewCritiquedTests, BatchBoundaryReviewTests, ReviewBatchFieldsFileTests, EscalationReachesBothRecordingCommandsTests and TheCloseCertifiesRatherThanReviewsTests): BG0441 (3), BG0499 (3), US0247 (3), US0560 (5), US0561 (1), US0562 (4), US0563 (1) and US0615 (2), then each is retired in the D0259 pattern (`Verify: manual - retired by US0918: <why>`, `Verified: manual (<date>) - retired, superseded by US0918`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node. A SprintReviewCritiquedTests case that pins the pre-constant read survives, and its stamp stays
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_no_stamp_names_a_deleted_test
  - **Verified:** yes (2026-09-26)

## Notes

- Deletes `critic.record_evidence`, `record_sprint_review`, `sprint_review_for`, `cmd_evidence`, `cmd_sprint_review` and the `coverage_state` branch; `sprint.cmd_review_batch`; the reads at `conformance.py` 455, 507 and 529 and `sprint_report.py` 1161, 1202, 1948 and 2230. `test_help_structure.py` (445) names a retired verb.
- Follow-up, not in scope: the `start_batch`/`close_batch` spans are left write-dead. Deleting them would add `lib/run_state.py` and `file_finding.py`.
- Lands after US0917.
- The shared prose edits to `help/sprint.md`, `reference-sprint-toolchain.md` and `reference-workflow-personas.md` moved to US0924.
- - Re-measured at 013a46d0: `record_evidence` 1213, `record_sprint_review` 2243, `sprint_review_for` 3134, `cmd_evidence` 4644, `cmd_sprint_review` 4783; `sprint.cmd_review_batch` 7807; evidence readers `sprint.py` 5166, 5476, 6154; batch-review readers `conformance.py` 427-428 and 461-462, `sprint.py` 5167, `sprint_report.py` 2202.
- The batch-review ledger is the only record that 253 Done stories were reviewed (239 of them from July), so it is read frozen rather than deleted: the date filter sits in `critic.sprint_review_for`, so every reader agrees. It reuses US0914's `REPAIR_VERB_RETIRED` rather than adding a second constant: the ledger's last row is 2026-09-21, before it (LC-008: one pin, not two).
- The evidence ledger no longer feeds critiqued (the two-role gate went with US0916), so it is simply unread.
- Lands after US0914 (the constant) and US0919.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points; AC3 fixture is a Done unit covered only by a sprint-review row and an evidence row, and adds the sprint report; stamps named (8 units, 22 criteria); batch spans recorded as a write-dead follow-up; Affects adds sprint_report.py, test_sprint_report.py, test_help_structure.py and the changelog fragment, and moves help/sprint.md, reference-sprint-toolchain.md and reference-workflow-personas.md to US0924 |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 grooming (engineering seat): AC2 and AC3 replaced with a frozen, date-licensed batch-review read after measuring that deleting it would strip critiqued from 184 Done stories; AC5 keeps a surviving pre-constant test's stamp |
