# US1343: The PRD, TRD and TSD describe the widened 6.5 and no longer say a token figure never stops a run

> **Status:** Ready
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Depends on:** US1332, US1333, US1334, US1335, US1336, US1337, US1338, US1339, US1340, US1233, US1234, US1235, US1294, US1295, BG1764
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_specs_v65.py, tools/tests/test_lean_trd_refresh.py, changelog.d/US1343.md
> **Epic:** EP0379
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose change board reads the specifications beside the release (Abena)
**I want** the PRD, TRD and TSD to describe what the widened 6.5 ships: the spend ceiling and
the effort by kind of unit, the cache measures, the release record and change failure rate,
the disclosure line and the person's ownership of the requirements documents
**So that** the specification the board reads describes the release it approves, and no spec
still states as a constraint what this release reverses

US1332 makes a spend appetite stop a run. The TRD lists "A token budget that gates" under
Won't Have and says tokens warn while minutes and units stop a run. The PRD's capacity row says
over-budget "WARNS, never gates", and the PRD's annex row will name a version US1334 replaces.
No spec names the cache measures, the release record, change failure rate, the disclosure
verb or who owns the PRD. This story amends rows and sentences and adds rows; RFC0063's
Non-Goals hold, so it rewrites no section.

## Acceptance Criteria

### AC1: the PRD's inventory names the widened cost controls

- **Given** the PRD's Feature Inventory once US1332 to US1338 and BG1764 are Done
- **When** its rows are read
- **Then** the Run appetite / breaker row names `--appetite-spend` and the spend axis. That axis
  is counted in priced input-equivalent tokens and warns at 75 and 95 per cent. At the appetite
  it stops cleanly at a unit boundary with exit 4. A meter that cannot read leaves it unjudged
  while minutes and units still stop the run. And `sprint.py appetite resize --spend` raises it
  only with `--decision`. The Sprint capacity row names `capacity.spend` and no longer says
  over-budget never gates. The Cost forecast and dispatch effort row names the `docs`, `bug`
  and `code` entries, stamped on each unit by its kind. The Cost anatomy row names the split of
  each role's cache writes into growth and re-writes after 5-minute and 1-hour expiry, and the
  reviewer recorded with its seat. A new row names the report's `cache_read_trend` and
  `cost_cache_writes` sections, the close's `cache-read` known issue for a fall of more than
  ten points, and `retro.py validate`'s demand. The Evidence annex row states the version
  `sprint_report.EVIDENCE_SCHEMA_VERSION` holds. Each row names its units, is Complete, names a
  Location that resolves, and names no `<script>.py <verb>` its script lacks. Fails on: the PRD
  at HEAD, where no row names `--appetite-spend`, `capacity.spend`, `cache_read_trend`,
  `cost_cache_writes` or a `docs` effort entry (`grep -cE` prints 0); its Sprint capacity row,
  "Over-budget WARNS, never gates" (line 285); its effort flags row, "The plan stamps both on
  every unit" (line 742); and an annex version other than the constant's, as the PRD's "at
  annex version 1.0" (line 333) will be once US1334 moves the constant to 1.1.
- **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_prd_names_the_widened_cost_controls
- **Caller:** n/a: the subject is the specification

### AC2: the PRD's inventory names the release record, the disclosure line and the person's ownership

- **Given** the same inventory once US1339, US1340, US1233, US1234, US1235, US1294 and US1295 are
  Done
- **When** its rows are read
- **Then** a row names the release record: the cut writes one record per version, naming its
  date and the reports signed since the previous release. The same or another row names
  change failure rate: the `escape.py` verb US1234 adds (read from its parser) counts the
  releases with a linked incident over the releases counted, names a release inside the settling
  period as pending, and reads not measured, never 0%, with no release or incident record; the
  sprint report and `retro.py seats` show it beside the CI-run rate. The Delegated and waiting
  signatures row names the `sprint_report.py` verb US1294 adds (read from its parser), which
  puts a disclosure line on a report already signed that still checks VALID, and RPT0030 to
  RPT0034. A new row says the person owns the PRD and the PVD and every other document the
  skill keeps. It says the Product Owner or Product Manager seat checks the work against its
  document under authority the person delegates and signs its review leg. It says the seat
  corrects a fact itself, proposes any change to a requirement, a priority or the scope as a
  change request the person decides, and asks when unsure. That row's Location names the seats
  section US1339 renames. Each row names its units (US1233, US1234, US1235; US1294, US1295;
  US1339, US1340). Fails on: the PRD at HEAD, which holds no "release record", "change failure",
  "person owns", "authority the person" or "settling" (`grep -ciE` prints 0), and whose
  Delegated and waiting signatures row names only `sprint.py sign --delegated --decision`.
- **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_prd_names_the_release_record_disclosure_and_ownership
- **Caller:** n/a: the subject is the specification

### AC3: the PRD's flags table lists the keys the widened release adds

- **Given** the PRD's Feature Flags table and `reference-config.md` once US1332 and US1336 are
  Done
- **When** the table is read
- **Then** it lists `capacity.spend`, `appetite.spend`, `routing.effort.docs`,
  `routing.effort.bug` and `routing.effort.code`, each with the default `reference-config.md`
  states (read with `config_defaults`). The spend keys' Effect says a set value stops the run at
  a unit boundary, counted in priced input-equivalent tokens, and that 0 sets no ceiling. The
  kind entries' Effect says each maps a role to an effort for units of that kind and ships
  empty. The capacity row no longer says tokens only warn without saying spend can stop a run.
  Fails on: the flags table at HEAD, which lists none of the five keys (`grep -cE` prints 0),
  and whose capacity row says "Tokens are a forecast and warn only; minutes and units feed the
  run breaker" (line 732).
- **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_prd_flags_list_the_widened_keys
- **Caller:** n/a: the subject is the specification

### AC4: the TRD records the spend breaker as a decision and names the release record

- **Given** the TRD once the feature stories are Done
- **When** §6, §10, §11 and §13 are read
- **Then** §13's Won't Have no longer lists a token budget that gates, and §10's cost-model
  paragraph no longer says tokens warn while minutes and units stop a run. A new ADR-015, the
  next number, records the spend appetite under D0637, with dollars, failing closed and reusing
  `capacity.tokens` as the alternatives. It says spend is counted in priced input-equivalent
  tokens, not dollars. It says the reading is a lower bound, so the breaker can fire late but
  never early. It says an unreadable meter leaves spend unjudged at that boundary and says why,
  while minutes and units still judge. And it says both keys ship at 0, and a raise needs a
  recorded decision. §6's committed records table gains the release record at the path
  `release_cut.py`'s code writes, with `release_cut.py` as its writer, read from the code in a
  fixture. The refresh scanner holds that record to its row: pending until this repository
  tracks one, and swept once the cut writes it. §6's annex sentence states the version
  `sprint_report.EVIDENCE_SCHEMA_VERSION` holds. The `run-state.json` row says the appetite
  carries the spend axis and the decision behind each spend raise, read from
  `run_state.appetite_record`. ADR-013's closing bullet names the `sprint_report.py` verb that
  gives RPT0029 to RPT0034 their lines, each still VALID. ADR-013 stays the one ADR citing
  D0503. Fails on: the TRD at HEAD, whose line 1545 lists "A token budget that gates.", whose
  line 917 says "tokens warn while minutes and units stop a run", which has no ADR-015 and no
  "release record" (each `grep -c` prints 0), and whose `run-state.json` row names no spend; and
  `test_every_committed_record_is_listed`, which refuses a listed path that tracks no file
  unless `pending_records()` holds it.
- **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_trd_records_the_spend_breaker_and_the_release_record
- **Caller:** `tools/tests/test_lean_trd_refresh.py`'s records sweep, which the cut's tree must
  pass once `release_cut.py` writes a record into it

### AC5: the TSD names the spend breaker's tests and the change failure rate

- **Given** the TSD once US1332 and US1234 are Done
- **When** its Quality Gates table and its Defect Management section are read
- **Then** the Scalability row for "the appetite breaker bounds an unattended run" also names
  the spend axis and the module that holds it, `test_loop_guard_spend.py`, covering the stop at
  the appetite, the 75 and 95 per cent warnings, the unread meter and the resolution order; the
  module and its tests are read from the tree. Defect Management gains a change failure rate
  passage. It names the `escape.py` verb (read from its parser), the releases with a linked
  incident over the releases counted, and a release inside the settling period as pending, the
  period read from `escape.py`'s code. It says the rate reads not measured, never 0%, with no
  release or no incident record. And it says the rate differs from the CI-run rate
  `deploy.py metrics` counts from the deploy ledger. Fails on: the TSD at HEAD, which holds no
  "spend", "change failure" or "settling" (`grep -ciE` prints 0), and whose Scalability row
  (line 444) trips the breaker only "when the appetite's minutes or units are spent".
- **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_tsd_names_the_spend_breaker_and_change_failure_rate
- **Caller:** n/a: the subject is the specification

## Notes

- Serves: Abena Osei, End goals 1, 2 and 3 (quoted under story 1), and Rowan Achterberg, who
  maintains the specs' scanners.
- RFC0063's Non-Goals hold: no rewrite of the Feature Inventory, the TRD or the TSD. Amend rows
  and sentences and add rows only. The Version and Coverage lines are the cut's (US1330).
- Add a row naming this unit to the PRD's Changelog, the TRD's Revision History and the TSD's
  Revision History, as US1329 did: `test_lean_prd_refresh.py`'s
  `test_every_prd_change_since_6_1_0_has_a_changelog_row` refuses a PRD commit whose unit no
  row names.
- `tools/tests/test_lean_trd_refresh.py` is in Affects for the release record.
  `test_every_committed_record_is_listed` fails a listed path that tracks no file unless
  `pending_records()` holds it, and fails a tracked file under a swept tree that no listed path
  matches. With no row, the cut's first record would turn that test red at US1330. Read the
  path from US1233's code, never typed here: it was not fixed at grooming.
- ADR-015: `test_the_trd_records_the_deferred_signature_ruling_as_an_adr` requires the ADR
  numbers to run from 1 with no gap, and D0503 to be cited by ADR-013 alone. ADR-015 cites
  D0637 and never D0503. The PRD's "forecast ... never a gate" (line 809) is about the forecast
  and stays true.
- Each new or amended inventory row must pass `test_lean_prd_refresh`'s `location_problems` and
  `unknown_commands`, which `test_lean_specs_v65` already imports.
- The `escape.py` and `sprint_report.py` verbs, the release record's path and the settling
  period were not fixed at grooming (see "Read this first"); the test reads each from the code.
- The existing specs module ran its 4 tests in 11.4 s at grooming, so the new tests have room
  under verify_ac's 120-second bound.

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | product seat | Groomed for run twenty-eight under D0638 |
| 2026-11-26 | orchestrator | Names RPT0029 beside RPT0030 to RPT0034 (D0640) |
