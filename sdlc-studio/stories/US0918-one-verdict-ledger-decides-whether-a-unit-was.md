# US0918: One verdict ledger decides whether a unit was reviewed

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer checking what is really done
**I want** a unit to count as reviewed when its latest delivery verdict is an independent APPROVE, with the evidence and sprint-review ledgers no longer read
**So that** one ledger answers 'was this reviewed', so status cannot disagree with itself across four files

## Acceptance Criteria

- **AC1:** Given `critic.py evidence`, `critic.py sprint-review` or `sprint.py review-batch`, when invoked, then each exits 2 with a message that it is retired naming `critic.py record` for a per-unit delivery verdict, and neither script's `--help` lists them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_ledger_verbs_are_retired
- **AC2:** Given a Done fixture story covered only by a batch row in `sprint-review-record.md`, when `conformance.py check` runs, then critiqued is unmet naming the missing independent APPROVE; with an independent delivery APPROVE recorded instead, it is met
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_critiqued_is_the_latest_delivery_approve
- **AC3:** Given `critic-evidence.md` and `sprint-review-record.md` present, when conformance, the gate and the close run, then neither file is read (each output is identical with them removed) and their bytes are unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_evidence_ledgers_are_frozen_and_unread
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py evidence`, `critic.py sprint-review` or `sprint.py review-batch` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_the_surface_names_no_retired_verb
- **AC5:** Given every criterion whose stamped Verify selector names a test this story deletes (SprintReviewCritiquedTests and the evidence and sprint-review record tests; at least those on US0247), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_verdict_ledger.py::OneVerdictLedgerTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
