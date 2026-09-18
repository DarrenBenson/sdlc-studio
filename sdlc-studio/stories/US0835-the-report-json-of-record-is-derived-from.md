# US0835: the report JSON of record is derived from the run's own artefacts, every figure carrying its source

> **Status:** Review
> **Delivers:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Epic:** EP0255
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the report JSON of record is derived from the run's own artefacts, every figure carrying its source
**So that** RFC0059 is delivered by work that can be planned and checked

## Acceptance Criteria

RFC0059's D1 is open, and this story pins it so the criteria can be checked: the report is a
META artefact - `RPT`, under `sdlc-studio/reports/` - registered in `sdlc_md.META_TYPES` beside
`review`, `retro` and `handoff`, which is the map that exists precisely for artefacts a run
RECORDS rather than delivers, carrying no acceptance criteria and sitting on no backlog. The
JSON is the artefact of record and the Markdown twin is committed beside it (D2a, settled).

THE FIXTURE RUN is shaped on RUN-01M2JA6J: 23 batch units summing 103 points, a recorded retro
with a carried table and rulings, critic verdict and evidence ledgers, a mutation ledger, a
verify report and a run record. What makes the derivation testable is that its artefacts
DISAGREE with each other in three places on purpose - the retro's prose, the run record and the
unit files - so a report that read the wrong one is caught by its figure rather than by an
assertion about where it looked.

The report's sections are RFC0059's settled list, shipped as `templates/core/sprint-report.md`;
this story derives the figures that fill them and US0836 renders them.

### AC1: every figure carries a resolvable source, and a sourceless figure refuses rather than prints

- **Given** THE FIXTURE RUN
- **When** `sprint_report.py build --run <the run id> --format json` runs through `main`
- **Then** every leaf figure in the JSON is an object carrying `value` and `source`, and each `source` names either a path that exists under the fixture root or a forge run id; a figure whose deriver produced no source makes the build exit 2 naming that figure's key and its section, and no JSON is written
- **Mutant:** pass a sourceless figure through instead of refusing the build - every figure then reads as carrying a source, none of them can be re-derived, and the Provenance section's whole claim ("a disputed number can be re-derived rather than argued") is false while reading as satisfied. Defaulting the missing source to the literal string `derived`, which this line named until 2026-09-18, SURVIVES: `_source_resolves` refuses `derived` as a source a reader cannot go to, so the build still exits 2 and the guard holds through its sibling clause rather than this one. Defence in depth, and not a mutant this criterion can be evidenced by
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ReportIsDerivedTests::test_every_figure_carries_a_resolvable_source
- **Verified:** yes (2026-09-18)

### AC2: the figures come from the run's artefacts, not from the retro's prose

- **Given** THE FIXTURE RUN, whose retro TEXT states `Delivered: 25 / 25` and 120 points while the run record's batch holds 23 units and the unit files' `Points:` fields sum to 103
- **When** the report is built
- **Then** `unit_count` is 23 sourced to the run record and `points_delivered` is 103 sourced to the unit files; the retro's path appears as the source of the rulings and the carried-open table and of nothing else
- **Mutant:** read the header counts from the retro's `Delivered: N / M` line - a hand-edited retro then rewrites the report's headline figures, and this repository has already shipped a retro header that contradicted its own batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ReportIsDerivedTests::test_figures_come_from_the_artefacts_not_the_retros_prose
- **Verified:** yes (2026-09-18)

### AC3: the stakeholder-consult section states what it renders while EP0256's schema is absent

- **Given** two copies of THE FIXTURE RUN: one carrying a consult artefact under `sdlc-studio/reviews/`, one carrying none - which is every run until EP0256 defines the schema, and is why the consult raised it against this story
- **When** the report is built on each
- **Then** with the artefact the section carries one entry per persona - name, perspective, verdict, finding - sourced to the consult's path; WITHOUT it the section is still present in the JSON and its value reads `NOT MEASURED` with the reason `no stakeholder consult artefact for this run`, and the build exits 0; the section is never dropped and never rendered as zero consults
- **Mutant:** omit the section when no consult artefact is found - a reader then cannot tell a run that consulted nobody from a report that forgot to look, which is the distinction the whole Not-proven discipline rests on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ReportIsDerivedTests::test_the_stakeholder_section_names_its_absent_schema
- **Verified:** yes (2026-09-18)

### AC4: the fingerprint covers the report's facts and not its signature or its timestamp

- **Given** one report built from THE FIXTURE RUN, carrying fingerprint F
- **When** it is rebuilt with only the generation timestamp advanced; rebuilt again after a signature block has been written into it; and rebuilt a third time after one unit's `Points:` is changed from 5 to 8
- **Then** the first two rebuilds return F unchanged, and the third returns a fingerprint that differs from F; the fingerprint's input is the ordered figure set alone, so a rebuild over an unchanged tree is byte-identical to its predecessor apart from the timestamp
- **Mutant:** fingerprint the whole JSON file - signing the report then changes the fingerprint the signature just recorded, so every sealed run reads INVALIDATED under US0845 from the moment it is signed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ReportIsDerivedTests::test_the_fingerprint_covers_the_facts_and_not_the_signature
- **Verified:** yes (2026-09-18)

### AC5: a figure states a measurement, so a mutation row the ledger reads as not-run is not counted as evidence

- **Given** a mutation ledger holding two killed rows for a unit, one whose anchor still occurs exactly once in its target and one whose anchor the file no longer holds - the state a unit reaches whenever a later fix moves a file its mutants were registered against, which is every unit of a run that repairs anything after registering
- **When** the report's evidence-by-unit figures are derived
- **Then** the unit counts one row, not two; the stale row is reported as its own term and never folded into the planned count, because `planned - killed` is the survivor figure and a survivor is a change no test failed on rather than a row nobody re-ran; and a unit whose every row is stale reads NOT MEASURED with staleness named, not `0/0`
- **Mutant:** count every row in the ledger - the page then publishes killed evidence for a mutant applied to bytes that exist nowhere, and it is the run's own later fixes that stale a row, so the figure is at its most wrong exactly when the page is derived; OR keep the stale rows in the planned count, which reports them as SURVIVORS and says a test failed to catch a change nobody applied; must redden on both
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StaleMutantRowsAreNotEvidenceTests
- **Verified:** yes (2026-09-18)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | default a missing `source` to the string `derived` - every figure then carries a source, none of them can be re-derived, and the Provenance section's whole claim ("a disputed number can be re-derived rather than argued") is false while reading as satisfied | every figure carries a resolvable source, and a sourceless figure refuses rather than prints |
| AC2 | read the header counts from the retro's `Delivered: N / M` line - a hand-edited retro then rewrites the report's headline figures, and this repository has already shipped a retro header that contradicted its own batch | the figures come from the run's artefacts, not from the retro's prose |
| AC3 | omit the section when no consult artefact is found - a reader then cannot tell a run that consulted nobody from a report that forgot to look, which is the distinction the whole Not-proven discipline rests on | the stakeholder-consult section states what it renders while EP0256's schema is absent |
| AC4 | fingerprint the whole JSON file - signing the report then changes the fingerprint the signature just recorded, so every sealed run reads INVALIDATED under US0845 from the moment it is signed | the fingerprint covers the report's facts and not its signature or its timestamp |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: four criteria. D1 pinned to a META `RPT` type under `sdlc-studio/reports/`. The fixture's artefacts disagree on purpose (retro prose 25 units / 120 points against a 23-unit, 103-point batch) so a wrong source is caught by its figure; the stakeholder section names EP0256's absent schema; the fingerprint excludes the signature and the timestamp. |
| 2026-09-18 | delivery | AC4 repaired against the shipped commands: `sign` then `sprint_report.py check` reported INVALIDATED on a legitimate seal, because three figures in the digest are facts the SEAL itself writes - each unit's Status, the run's `ended_at`/`duration_hours`, and a delivered count taken from statuses. `OUTSIDE_THE_DIGEST` now names them with their reason, one predicate serves both the fingerprint and `revalidate`, and `terminal_summary` counts units that CLEARED THEIR TERMINAL GATE - the fact that is true when the page is derived and that the signature does not move. Found by exercising the CLI end to end, not by any test in the batch; pinned now by `TheSealIsATransactionTests::test_the_seal_does_not_invalidate_the_report_it_signs` with its mutant killed. |
| 2026-09-18 | CLI exercise | AC5 added. `_mutants_by_unit` counted every row in the mutation ledger, including rows the ledger itself reads as NOT-RUN because the mutant was applied to bytes the file no longer holds. A run's own later fixes are what stale a row, so a page derived at the end of a repairing run was the most likely to state evidence nobody had. The report now judges each row at the ledger's own grain - the anchor's site, via `mutation.row_staleness` - and stale rows are neither evidence nor survivors. Measured on this run: all 33 rows are live at the anchor grain, so the figures are unchanged and the claim is now checked rather than assumed. |
| 2026-09-18 | re-mutation | AC1's declared mutant replaced after it SURVIVED on re-execution. Defaulting a missing source to `derived` cannot produce a passing build, because the resolution check refuses `derived` in the next clause - so the criterion was evidenced by a mutant its own guard could not be falsified by. The row now names the change AC1's Then clause actually turns on: the sourceless figure passing through. US0835's four earlier rows were dropped by LL0053 when `_mutants_by_unit` moved and were re-executed from their declared prose, not transcribed. |
