# US0960: Every report signed before the tracked record checks valid in a clean clone once migrate files its record

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py, sdlc-studio/reports/runs/RUN-01M36R3D.json, sdlc-studio/reports/runs/RUN-01M3891F.json, sdlc-studio/reports/runs/RUN-01M39MC0.json, sdlc-studio/reports/runs/RUN-01M3BK9Y.json, sdlc-studio/reports/runs/RUN-01M3CK1K.json, sdlc-studio/stories/US0941-a-report-maya-signed-still-validates-after-the.md, .github/workflows/lint.yml, changelog.d/US0960.md
> **Epic:** EP0267
> **Parent:** CR0599
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer upgrading a project that signed sprint reports before the record was tracked
**I want** `migrate --apply` to file the tracked record for each signed report whose run record lives only in `.local`, with its review rows and CI runs frozen as the page read them
**So that** the reports I already signed check in any clone after the upgrade, and US0941 AC5 is executable again

## Acceptance Criteria

- **AC1:** Given a fixture project with a signed schema-2 report whose run record is only in `.local/run-archive`, when `migrate` runs without `--apply`, then it lists the record as a deterministic item and writes nothing, and with `--apply` it writes `sdlc-studio/reports/runs/<RUN-ID>.json`. Fails on: writing in a dry run, or reading only the live record and skipping archived runs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::SignedRecordMigrationTests::test_migrate_files_the_record_of_a_signed_report
- **AC2:** Given the migrated fixture committed and cloned without `.local`, with a stub `gh` on PATH answering a push run inside the window, when `check` runs, then it exits 0. Fails on: filing the record without freezing its CI runs, so the clone re-reads the forge (RPT0010 read INVALIDATED that way: `dora_value[0]` signed 72, now 7)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::SignedRecordMigrationTests::test_a_migrated_record_checks_in_a_clean_clone
- **AC3:** Given a record already filed, when `migrate --apply` runs again, then the file is byte-identical. Fails on: re-freezing from today's ledger and forge, which moves a signed figure on every upgrade
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::SignedRecordMigrationTests::test_migrate_never_rewrites_a_filed_record
- **AC4:** Given a signed report whose frozen inputs would not re-derive to its fingerprint (a counted row superseded since), when `migrate` runs, then it names that report as needs-a-human and files nothing for it. Fails on: filing a record that turns a report VALID in the signing clone into INVALID in every clone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::SignedRecordMigrationTests::test_a_report_that_would_not_rederive_is_named_not_filed
- **AC5:** Given this repository after the change, when a full-history clean clone of HEAD with a stub `gh` answering a push run in every window runs `check` on RPT0006-RPT0010, then each exits 0; US0941 AC5's Verify is re-pointed at this selector in the same commit. Fails on: the migration not run and committed here, or the `ci` job's depth-1 checkout (the test and CI would see no history)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py::TrackedRunRecordTests::test_this_repos_signed_reports_check_in_a_clean_clone

## Notes

- Depends on: US0959, BG0795, BG0788, BG0790, BG0785
- Decomposed from CR0599. Scope of the history: RPT0001 is not filed; RPT0002, RPT0003 and RPT0005 are schema 1 and stand as filed (exit 2 by design); RPT0004 is unsigned and superseded. So this repo migrates RPT0006-RPT0010, and any rc.1 project migrates its own (the web repo's soak sprint signs under rc.1; runbook step 19). Frozen as the page read them: `review_rows` by the BG0787 rule, which reads all five VALID today, and `ci_runs` from the stale `.local/ci-runs.json` rows inside each window, which is empty for all five, so DORA re-derives exactly as signed. The frozen-input function is the one PREPARE uses (BG0795, BG0788). Re-point US0941 AC5 at AC5's selector in the landing commit, NOT at plan time: the release verify lane runs every Done story's criteria and would read a not-yet-written test red. Sets `fetch-depth: 0` on lint.yml's `ci` job checkout. If BG0788 is cut, this freezes CI runs only and rounds keep the BG0787 rule. Serialise on migrate.py after BG0790 and BG0785. Ratchet: no check added; the migration step is deterministic and reported like migrate's others.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (US0960) |
