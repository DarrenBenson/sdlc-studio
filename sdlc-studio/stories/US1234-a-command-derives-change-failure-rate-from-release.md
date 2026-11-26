# US1234: A command derives change failure rate from release records and linked incidents, never reading 0% unmeasured

> **Status:** Ready
> **Depends on:** US1233, US1294
> **Risk-class:** elevated
> **Delivers:** CR0695
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/deploy.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py, changelog.d/US1234.md, sdlc-studio/reviews/command-audit.md
> **Epic:** EP0339
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who takes each release to the change board (Abena)
**I want** a command that derives change failure rate from the release records and the incident
issues linked to them, naming the releases counted, the failed ones with their incidents, the
ones still settling and the window
**So that** the figure I show the board traces to records, and reads not measured, never 0%,
where nothing was recorded

## Context

### Background

D0458: change failure rate is the releases with at least one linked incident divided by the
releases counted. D0457: an incident is an issue with a root-cause section, triaged into the
escaped bugs that name the release they shipped in. US1233 writes the release record this command
reads. `escape.py` already holds the escape record's verbs (`trace`, `to-class`), so the rate is
a third verb there: `escape.py failure-rate`.

---

## Acceptance Criteria

### AC1: the rate names the releases counted, the failed release with its incident, and the window

- **Given** a project whose `sdlc-studio/reports/releases.jsonl` holds 1.0.0, 1.1.0, 1.2.0 and 1.3.0, each dated between 2026-01-01 and 2026-03-16; an issue IS0001 with a written `## Root Cause` section and `Decomposed-into: BG0001`; and BG0001 carrying `Escaped: yes`, `Shipped-in: v1.1.0` and `Parent: IS0001`
- **When** `escape.py failure-rate --since 2026-01-01 --until 2026-03-31` runs, as text and with `--format json`
- **Then** it states 25% (1 of 4 releases), names the four releases counted, names 1.1.0 as failed with IS0001 and BG0001, and names the window 2026-01-01 to 2026-03-31 and the 14-day settling period; the JSON carries the same values. Fails on: HEAD, where `escape.py failure-rate` exits 2 with `invalid choice: 'failure-rate' (choose from 'trace', 'to-class')`; a bare percentage; or a release counted as failed for an escaped bug no incident names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_the_rate_names_the_releases_counted_the_incident_and_the_window
- **Caller:** `escape.py failure-rate`, the operator's command; `sprint_report.py` and `retro.py seats` call the same function (US1235)

### AC2: a release inside the settling period is pending

- **Given** the same records and a fifth release, 1.4.0, dated 2026-03-25 (six days before the window's end)
- **When** the command runs over the same window, then again with `--settle-days 3`
- **Then** the first run lists 1.4.0 as pending inside the 14-day settling period, in neither the releases counted nor the failed ones, and still states 25% (1 of 4); the second counts 1.4.0 as settled and states 20% (1 of 5). Fails on: HEAD, which has no such verb; or a young release counted as a success, which lowers the rate before an incident could be linked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_a_release_younger_than_the_settling_period_is_pending
- **Caller:** `escape.py failure-rate --settle-days N`

### AC3: no release record, or no incident record, reads not measured and never 0%

- **Given** three projects over the same window: one whose record file holds no release dated in it; one with four settled releases and no issue whose `## Root Cause` section is written (its one issue holds only the scaffold sentence `file_finding.ROOT_CAUSE_SCAFFOLD`); and one with four settled releases and an incident issue whose escaped bug shipped in a release outside the window
- **When** the command runs in each
- **Then** the first two print `not measured:` with a reason naming what is absent (no release record in the window; no incident recorded) and no percentage, each exiting 0, and the third states 0% (0 of 4) naming the four releases. Fails on: HEAD, which has no such verb; 0% for a project that records no incident; or not measured where incidents are recorded and none is linked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_no_release_or_no_incident_record_reads_not_measured
- **Caller:** `escape.py failure-rate`; US1235 carries the same reason onto the report

### AC4: the help names the command and how its rate differs from the deploy ledger's

- **Given** `help/deploy.md` and the `escape.py` section of `reference-scripts-review.md`
- **When** they are read
- **Then** the deploy help's Commands table has a row for `escape.py failure-rate` naming its window and settling period flags and defaults, its sources (the release records `release_cut.py changelog-cut` writes and incident issues linked through the escaped bugs they were triaged into), and saying it counts releases with a linked incident where `deploy.py metrics` counts `failed` and `rolled-back` rows of the deploy ledger; and the reference section names the verb. Fails on: HEAD, where `grep -c failure-rate` prints 0 for both files, leaving two figures called change failure rate with nothing to tell them apart
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_the_deploy_help_names_the_command_and_its_sources
- **Caller:** `help/deploy.md`, the page `/sdlc-studio deploy` loads, and `reference-scripts-review.md`, the script catalogue

---

## Scope

### In Scope

- `escape.py failure-rate [--since D] [--until D] [--settle-days N] [--format text|json]`, read-only
- One function the verb prints and US1235 calls, so no second calculation exists
- The deploy help row and the reference paragraph

### Out of Scope

- The report section and the seat scorecard (US1235)
- An incident marker or Root Cause scaffold on new issues (US1253, EP0346, not in v6.5.0)
- A configuration key for the window or the settling period
- A gate: the figure is advisory, as `deploy.py metrics` is

---

## Technical Notes

- Grounded at HEAD af477fc6d on 2026-11-26. `escape.py` exposes `trace` and `to-class` only; no script reads a release record (US1233 adds it) and no issue in this repository carries a Root Cause section.
- An incident (D0457) is an issue under `sdlc-studio/issues/` whose `## Root Cause` section is written: not empty and not the scaffold sentence `file_finding.ROOT_CAUSE_SCAFFOLD`, the same test `transition._escaped_root_cause_gate` applies to a bug. It is linked to a release through each bug it was triaged into, named by the issue's `Decomposed-into` or naming the issue as its `Parent` (both written by `triage.py`), that carries `Escaped: yes` and a `Shipped-in`. When US1253 later scaffolds the section, an unfilled one reads as unwritten.
- A `Shipped-in` of `v1.1.0` and a record of `1.1.0` are one release: drop one leading `v`, as `escape.release_tag` treats the two spellings.
- Defaults: the window is the 90 days ending today; the settling period is 14 days. Flags override both; no configuration key is read, so `test_lean_config_keys_read` needs no reference-config or config-defaults change.
- Expose one function (for example `escape.failure_rate(root, since, until, settle_days)`) returning the rate, the releases counted, failed (each with its incidents and bugs), pending, the window, the period and any not-measured reason. US1235 reads that function.
- `sprint_report.NON_CEREMONY_VERBS["escape"]` must gain the verb: `test_sprint_report.py::...::test_escape_declares_every_verb_its_parser_exposes` pins that tuple to `escape.py`'s parser. That one line is this unit's only change to `sprint_report.py`.
- `reference-scripts-surface.md` is generated: run `docgen.py surface` (the budgets lane runs `--check` when a script is staged).
- Three figures carry the name: the report's DORA row (CI push runs, `sprint_report.py`), `deploy.py metrics` (the deploy ledger) and this one (releases with a linked incident). The help says which is which.
- New test module carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/escape.py`; fixtures are plain files and need no git.
- Run twenty-eight: `sprint_report.py` is edited in turn by US1334, US1338, US1294, this story and US1235; `reference-scripts-surface.md` by US1294 and this story.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| A record line does not parse | Exit 2 naming the line; no rate is printed |
| Two escaped bugs from one incident shipped in the same release | The release fails once |
| One incident's bugs shipped in two releases | Both releases fail |
| An escaped bug names a release no record holds | It moves no figure and is named as linked to an unrecorded release |
| Every release in the window is still settling | Not measured, naming the pending releases |
| `--since` is after `--until`, or a date does not parse | Exit 2 naming the flag |

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| US1233 | Blocking | The release record this command reads | Draft |
| US1294 | Sequencing | Edits `sprint_report.py` and `reference-scripts-surface.md` before this story | Draft |
| US1235 | Downstream | Shows this command's figure on the report and the scorecard | Draft |

---

## Open Questions

- [ ] Are a 90-day window and a 14-day settling period the defaults the board wants? Each is one constant and a flag. - Owner: operator

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Re-grounded against HEAD for run twenty-eight (D0638) |
| 2026-11-26 | orchestrator | Affects names sdlc-studio/reviews/command-audit.md (and, for US1333, `test_artifact.py`), the registry the plan says a new flag implies |
