# US0995: A consumer reads the lesson class store, the evidence logs and the four ledgers against the annex

> **Status:** Draft
> **Delivers:** CR0609
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_ledgers.py, changelog.d/US0995.md
> **Epic:** EP0275
> **Points:** 3
> **Depends on:** US0992, CR0619
> **Persona:** Maya Okafor

## User Story

**As** a team lead charting estimate accuracy and review outcomes across sprints
**I want** the lesson rows, the actuals, forecast and audit-cost lines, and the critic, velocity, decisions and deploy tables documented in the annex
**So that** a chart built over them survives a skill upgrade, or the upgrade names the field that moved

## Acceptance Criteria

- **AC1:** Given an actuals line written by `telemetry.py record`, a forecast line written by `telemetry.py forecast`, an audit-cost line written by `audit_cost.py record` and a lesson row written by `retro.py extract`, when the conformance test reads each against the annex, then every field each holds is documented and every field the annex marks required is present.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_ledgers.py::LedgerAnnexTests::test_written_lines_conform_to_the_annex
- **AC2:** Given the critic, velocity, decisions and deploy ledgers as `critic.py record`, `retro.py accuracy --write`, `decisions.py add` and `deploy.py record` create them in a fixture, when their header rows are compared with the annex's table layouts, then each column list is equal, in order, the critic table's with nine columns.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_ledgers.py::LedgerAnnexTests::test_ledger_headers_match_the_annex

## Notes

- Release: 6.2 (D0355 breakdown G1, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: a field added to telemetry.FIELDS or audit_cost.LEDGER_FIELDS, or a key added to a lesson row, with no annex line
- AC2 must fail on: a column added to the critic delivery table or the velocity header with no annex change
- Serves Jonah's End goal 4 (jonah-reyes-team-lead.md:29).
- Builds after CR0619 (G6)'s ninth-column story, so the annex documents nine critic columns from the start rather than bumping its version on arrival.
- Writers and field lists at HEAD: telemetry.FIELDS (telemetry.py:99) plus the stamped project; record_forecasts (telemetry.py:677, fed by sprint.record_forecast at sprint.py:1790); audit_cost.LEDGER_FIELDS (audit_cost.py:66); lesson rows (lessons.py:1742, no field tuple, so the test reads a written row); critic `_HEADERS` (critic.py:68); retro VELOCITY_HEADER (retro.py:825); deploy.py:85; templates/decisions.md. Driven through each CLI rather than the constants alone (LL0040).
- The annex documents the legacy row widths a reader meets: critic.py reads 8-, 7-, 6- and 5-column rows, and this repository's ledger holds them. Earlier rows are padded, never rewritten.
- decisions.md's in-cell markers: `[kind: ...]` and the trailing `[authorised by: ...]` (decisions.py:357-373) are documented, with the authoriser last; any other marker, including G5's planned `[until: ...]`, is named uncontracted until it ships.
- deploy-log.md does not exist in this repository; it is a consuming-project ledger, so the fixture creates it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G1 after the refine panel's review |
