# US0918: One verdict ledger decides whether a unit was reviewed

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py, changelog.d/US0918.md
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
- **AC2:** Given a Done fixture story covered only by a batch row in `sprint-review-record.md`, when `conformance.py check` runs, then critiqued is unmet naming the missing independent APPROVE; with an independent delivery APPROVE recorded instead, it is met. Fails on: HEAD, where the sprint-review row satisfies critiqued
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_critiqued_is_the_latest_delivery_approve
- **AC3:** Given a Done unit with no per-unit verdict, covered only by a `sprint-review-record.md` row and a `critic-evidence.md` row, when conformance, the gate, the close and the sprint report run, then neither file is read (each output is identical with them removed) and their bytes are unchanged. Fails on: removing conformance's read while `sprint_report.py` still counts the evidence rows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_evidence_ledgers_are_frozen_and_unread
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py evidence`, `critic.py sprint-review` or `sprint.py review-batch` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_surface_names_no_retired_verb
- **AC5:** Given the criteria whose stamped Verify selector names a test this story deletes (EvidenceTests, SprintReviewCritiquedTests, BatchBoundaryReviewTests, ReviewBatchFieldsFileTests, EscalationReachesBothRecordingCommandsTests and TheCloseCertifiesRatherThanReviewsTests): BG0441 (3), BG0499 (3), US0247 (3), US0560 (5), US0561 (1), US0562 (4), US0563 (1) and US0615 (2), then each is retired in the D0259 pattern (`Verify: manual - retired by US0918: <why>`, `Verified: manual (<date>) - retired, superseded by US0918`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_no_stamp_names_a_deleted_test

## Notes

- Deletes `critic.record_evidence`, `record_sprint_review`, `sprint_review_for`, `cmd_evidence`, `cmd_sprint_review` and the `coverage_state` branch; `sprint.cmd_review_batch`; the reads at `conformance.py` 455, 507 and 529 and `sprint_report.py` 1161, 1202, 1948 and 2230. `test_help_structure.py` (445) names a retired verb.
- Follow-up, not in scope: the `start_batch`/`close_batch` spans are left write-dead. Deleting them would add `lib/run_state.py` and `file_finding.py`.
- Lands after US0917.
- The shared prose edits to `help/sprint.md`, `reference-sprint-toolchain.md` and `reference-workflow-personas.md` moved to US0924.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points; AC3 fixture is a Done unit covered only by a sprint-review row and an evidence row, and adds the sprint report; stamps named (8 units, 22 criteria); batch spans recorded as a write-dead follow-up; Affects adds sprint_report.py, test_sprint_report.py, test_help_structure.py and the changelog fragment, and moves help/sprint.md, reference-sprint-toolchain.md and reference-workflow-personas.md to US0924 |
