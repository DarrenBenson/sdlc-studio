# US0917: The operator's signature seals the run without a per-unit sign-off row

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator signing a finished sprint
**I want** `sprint sign` to move the batch to its terminal statuses and write the one run signature, with no per-unit sign-off rows and no close preflight
**So that** one signature means one signature: 22 rows were written after D0255 said the operator signs once

## Acceptance Criteria

- **AC1:** Given a closed fixture run whose batch units sit at Review with independent delivery APPROVEs and green criteria, when `sprint.py sign --principal <operator>` runs, then every unit reaches its terminal status, the run signature is written, and `signoff-record.md` gains no row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_sign_writes_no_signoff_rows
- **AC2:** Given one batch unit whose criteria are red, when `sprint.py sign` runs, then it stops naming that unit and its refused terminal gate, and the run is left open
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_sign_still_stops_on_a_red_unit
- **AC3:** Given `sprint.py preflight`, when invoked, then it exits 2 with a message that it is retired naming `sprint.py close`, and `sprint.py --help` does not list it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_preflight_is_retired
- **AC4:** Given a rendered sprint report and the report templates, then none carries a per-unit sign-off column or an awaiting-sign-off count
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_the_report_carries_no_per_unit_signoff
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `sprint.py preflight` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_the_surface_names_no_retired_verb
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (the apply-signoff, stop-awaiting-signoff, close-preflight and preflight-count classes in `test_sprint.py`; at least those on BG0285, BG0286, BG0589, US0389, US0445, US0624, US0638, US0643), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
