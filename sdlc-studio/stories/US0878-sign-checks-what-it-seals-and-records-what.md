# US0878: Sign checks what it seals and records what actually happened

> **Status:** Done
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py
> **Epic:** EP0260
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator signing off a sprint
**I want** sign to check that what it seals is the run's report on the tree the close left, and to record what actually happened
**So that** my signature cannot land on a stale page, and a partial run is never mistaken for an abort

## Acceptance Criteria

- **AC1:** Given a run whose recorded report is RPTa, when sprint sign names RPTb, then it refuses naming both
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py::SignChecksTests::test_sign_refuses_a_report_that_is_not_the_runs
  - **Verified:** yes (2026-09-23)
- **AC2:** Given tracked files changed in content since the close, other than the files the signature itself writes, when sprint sign runs, then it refuses naming the files; with the tree as the close left it, it signs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py::SignChecksTests::test_sign_refuses_a_tree_changed_since_close
  - **Verified:** yes (2026-09-23)
- **AC3:** Given a partial or missed goal verdict, when the run is signed, then the archived outcome is partial or missed, never stopped
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py::OutcomeTests::test_a_signed_partial_run_is_not_labelled_stopped
  - **Verified:** yes (2026-09-23)
- **AC4:** Given sprint stop without --force and no pending decision, then the recorded cause is the operator, not pending-decision
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py::OutcomeTests::test_a_plain_stop_records_the_operator_as_cause
  - **Verified:** yes (2026-09-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
