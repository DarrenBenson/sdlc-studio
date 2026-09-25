# US0917: The operator's signature seals the run without a per-unit sign-off row

> **Status:** Done
> **Depends on:** US0916 - the two-role gate reads the sign-off ledger (EP0263 readiness)
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py, changelog.d/US0917.md, .claude/skills/sdlc-studio/help/sprint.md, sdlc-studio/bugs/BG0292-the-close-status-stamp-is-rung-blind-it.md, sdlc-studio/bugs/BG0488-us0608-and-us0609-ship-a-feature-no-cli.md, sdlc-studio/bugs/BG0528-a-delivered-unit-left-at-ready-is-invisible.md, sdlc-studio/bugs/BG0582-the-design-rung-can-be-planned-and-groomed.md, sdlc-studio/bugs/BG0589-the-close-pre-flight-counts-advisory-rows-as.md, sdlc-studio/stories/US0236-sprint-close-apply-signoff-records-per-unit-sign.md, sdlc-studio/stories/US0274-the-preflight-covers-the-apply-signoff-prerequisites-per.md, sdlc-studio/stories/US0468-help-sprint-md-documents-the-run-lifecycle-batch.md, sdlc-studio/stories/US0602-a-panel-signed-unit-is-distinguishable-from-an.md, sdlc-studio/stories/US0626-an-unfinished-batch-unit-holds-the-close-through.md, sdlc-studio/stories/US0638-the-close-pre-flight-runs-the-retro-checklist.md, sdlc-studio/stories/US0639-every-gate-execution-the-close-runs-is-recorded.md, sdlc-studio/stories/US0645-the-operator-summary-is-derived-from-the-record.md, sdlc-studio/stories/US0823-every-other-route-that-ends-a-run-reads.md, sdlc-studio/stories/US0832-close-splits-into-prepare-which-does-everything-that.md, sdlc-studio/stories/US0833-sign-writes-the-principal-the-date-and-the.md
> **Epic:** EP0263
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** operator signing a finished sprint
**I want** `sprint sign` to move the batch to its terminal statuses and write the one run signature, with no per-unit sign-off rows and no `sprint.py preflight` verb
**So that** one signature means one signature: 22 rows were written after D0255 said the operator signs once

## Acceptance Criteria

- **AC1:** Given a closed fixture run whose batch units sit at Review with independent delivery APPROVEs and green criteria, when `sprint.py sign --principal <operator>` runs, then every unit reaches its terminal status, the run signature is written, and `signoff-record.md` gains no row; the same run with one unit whose criteria are red, or one unit with no independent delivery APPROVE, stops naming that unit and its unmet bar and leaves the run open. Fails on: HEAD's `_apply_signoff` writing a row per unit, and on a deletion that lets sign seal an unreviewed or red unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_sign_writes_no_signoff_rows
  - **Verified:** yes (2026-09-25)
- **AC2:** Given `sprint.py preflight`, when invoked, then it exits 2 with a message that it is retired naming `sprint.py close`, and `sprint.py --help` does not list it; `close_preflight` still runs inside `sprint.py close`. Fails on: deleting `close_preflight` with the verb
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_preflight_is_retired
  - **Verified:** yes (2026-09-25)
- **AC3:** Given a closed fixture run, then `sprint_report.py checklist` has no per-unit sign-off row, `operator-summary` shows no per-unit sign-off capacity, `sprint.py stop` reports no awaiting-sign-off count, and the close-status block does not say sign-off is owed per unit. Fails on: removing the checklist row while `_signoff_owed` still feeds `stop` and the close status
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_the_report_carries_no_per_unit_signoff
  - **Verified:** yes (2026-09-25)
- **AC4:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `sprint.py preflight` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_the_surface_names_no_retired_verb
  - **Verified:** yes (2026-09-25)
- **AC5:** Given the criteria whose stamped Verify selector names a test this story deletes (the apply-signoff, stop-awaiting-signoff, close-preflight and preflight-count classes in `test_sprint.py`, among them ApplySignoffBatchCoverageTests, ApplySignoffRequestDerivationTests, CloseDoesNotForecloseSignoffTests, ClosePreflightDriftTests, OnePreflightCountReadByBothRenderersTests, PreflightCoverageCountsTests, PreflightChecklistTests and CloseCostRecordingTests): BG0285 (2), BG0286 (2), BG0589 (4), BG0702 (the preflight and unanswered-unit tests), US0389 (1), US0445 (4), US0624 (3), US0638 (6) and US0639 (7), then each is retired in the D0259 pattern (`Verify: manual - retired by US0917: <why>`, `Verified: manual (<date>) - retired, superseded by US0917`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py::SignSealsOnceTests::test_no_stamp_names_a_deleted_test
  - **Verified:** yes (2026-09-25)

## Notes

- The old AC2 (sign stops on a red unit) and the readiness review's new AC7 (sign stops on a unit with no independent APPROVE) both keep existing stops and pass at HEAD. Neither is a new check under the ratchet rule. Engineering call: they are the control half of AC1, which keeps the story at five criteria.
- Deletes `_apply_signoff` (6411-6603), `cmd_preflight`, its parser and `_render_preflight`, `_signoff_preflight`, `_signoff_owed` and `sprint_report._ck_signoff`. `close_preflight` stays, and so does `blocked_by_pending`: `stop` reads it, and its awaiting-sign-off half went with US0916.
- Every sign-off read in `sprint_report` belongs to this story; US0919 keeps only the delegated-row check. Lands after US0916 and before US0918 and US0919, because it removes `sprint`'s calls to `critic.record_signoff` before US0919 deletes it.
- Engineering call: US0643's stamps retire with US0919, whose panel classes they name.
- Size 8 at the cap. Splitting out the preflight verb would not buy parallelism: it is the same file.
- `lib/run_state.py` (docstrings only) leaves Affects. The shared prose edit to `help/sprint.md` moved to US0924.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 5 -> 8 points; user story names no `sprint.py preflight` verb; the red-unit stop and the new unreviewed-unit stop are AC1's control; the report criterion names checklist, operator-summary, stop and close status; stamps named, BG0702 and US0639 added; Affects adds test_help_structure.py, test_lean_sign.py and the changelog fragment, drops lib/run_state.py and moves help/sprint.md to US0924 |
| 2026-09-25 | Engineering seat | Delivery: AC5 is scoped to the test nodes actually deleted. BG0285 (`reopen_run`), BG0286 (`_batch_unfanned_units`, `_batch_story_units`), US0389 (installed-copy drift in `close_preflight`), US0445 (`_derive_parent_requests`), US0624 (`uncovered_units`), US0638 AC1-AC5 and US0639 AC1-AC6 (`close_preflight`) and BG0589 AC1 and AC3 (`preflight_headline` and `_report_preflight`) test code that survives, so their stamps stay live; BG0702 is Superseded and was never stamped. Notes: `blocked_by_pending` is kept |
