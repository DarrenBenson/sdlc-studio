# US0914: A standing REJECT clears only by a round-2 APPROVE or by carrying the unit

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer answering a review
**I want** a REJECT to have exactly two exits, a round-2 APPROVE from the reviewer who rejected or carrying the unit as a known issue at the cap
**So that** no unit is argued through a repair ledger's closures, and every rejected unit ends either approved or visibly carried

## Acceptance Criteria

- **AC1:** Given `critic.py repair`, when invoked, then it exits 2 with a message that it is retired naming the two exits (a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the review cap), and `critic.py --help` does not list it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_repair_verb_is_retired
- **AC2:** Given a fixture unit whose standing delivery REJECT has every finding closed by a row in a pre-existing `repair-record.md`, when it is moved to Done, then it is refused as an unanswered REJECT and the refusal names the two exits, not `critic.py repair`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_a_repair_row_no_longer_answers_a_reject
- **AC3:** Given the same REJECT answered by a round-2 independent APPROVE from the rejecting reviewer, then Done succeeds and conformance reports the unit critiqued; given a round-2 REJECT instead, then the unit is carried (dropped from the batch with a filed bug) as Sprint 1 built it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_two_exits_still_work
- **AC4:** Given `repair-record.md` present, when conformance, the close and the sprint report run, then none reads it (each output is identical with the file removed) and its bytes are unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_repair_ledger_is_frozen_and_unread
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py repair` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (the repair, partial-repair and closure classes in `test_critic.py`; at least those on BG0607, BG0618, BG0629, BG0677, US0314, US0319, US0620, US0622, US0627), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_ledger.py::RepairLedgerGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
