# US0962: The migration to v6 is rehearsed on two real consuming projects, and the record is published

> **Status:** Draft
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/upgrade-rehearsal-v6.md, tools/tests/test_lean_upgrade_rehearsal_record.py, changelog.d/US0962.md
> **Epic:** EP0267
> **Points:** 3
> **Persona:** Jonah Reyes

## User Story

**As a** team lead with a project that has not moved since v4 or earlier
**I want** evidence that `migrate` carries a real, old, busy project to v6, with what it left to a human
**So that** I upgrade knowing what I will meet, not from a fixture's promise

## Acceptance Criteria

- **AC1:** Given scratch copies of two real consuming projects on this machine, one recording skill 4.1.0 (schema 2, 688 stories) and one recording 2.4.1 (schema 2, 594 stories, with frozen sign-off records), when `migrate` then `migrate --apply` run under the 6.0.0-rc.1 skill, then `docs/upgrade-rehearsal-v6.md` holds one table row per project, labelled by its recorded version and never by name, giving the version before and after, each command with its exit code, what `--apply` changed, what it left to a human, and the `validate.py check` and `gate.py` exit codes before and after. Fails on: a record written from the dry run alone
  - **Verify:** pytest tools/tests/test_lean_upgrade_rehearsal_record.py::UpgradeRehearsalRecordTests::test_each_project_row_records_both_commands_and_their_exit_codes
- **AC2:** Given the record's Findings table, then every row carries a bug, change request or decision id that resolves in this workspace, filed with `file_finding.py`. Fails on: a refusal or failure described in prose with no owner, which the 6.0.0 notes would then have to disclose by hand
  - **Verify:** pytest tools/tests/test_lean_upgrade_rehearsal_record.py::UpgradeRehearsalRecordTests::test_every_finding_row_names_an_owner_that_resolves

## Notes

- Depends on: BG0785, BG0790
- The rc.1 notes promised it in public: 'the migration is rehearsed on two real consuming projects, with the record linked from the 6.0.0 notes'. Measured 2026-09-27: the v4.1 project's .version records skill 4.1.0 (upgraded from 3.1.0), the v2.4 project's 2.4.1 (from 1.4.0); neither carries a retired DoD check tag; the v2.4 project holds 3 frozen review records. The two projects are the ones the Sprint 6 product seat measured (s6 scratchpad); the record and every tracked file name them only by version (neutrality lane). The rehearsal copies each repository into scratch (`git clone --local`), never writes the originals, and runs the installed rc.1 skill (`~/.claude/skills/sdlc-studio/scripts/migrate.py`), not the dev checkout. It exercises the multi-hop path no fixture covers (schema 2, v2-era and v4-era artefacts, 600+ stories). Every defect is filed here as an rc.1 finding; a High blocks the cut. Runs after BG0785 (migrate names a conformance cutoff for a v4-era project) and BG0790 (the version stamp keeps the suffix). US0955 and US0953 link the record. Ratchet (LC-008): a one-off record, no pinned test. Absorbs QA's Q5 (D0278). Rehearse on COPIES only; homelab has 35 `shell ssh` Verify lines, so never run gate --release or verify_ac run there.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (US0962) |
