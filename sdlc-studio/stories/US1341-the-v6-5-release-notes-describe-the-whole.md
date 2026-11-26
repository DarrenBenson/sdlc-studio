# US1341: The v6.5 release notes describe the whole widened release, from the spend ceiling to the release record

> **Status:** Ready
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Depends on:** US1332, US1333, US1334, US1335, US1336, US1337, US1338, US1339, US1340, US1233, US1234, US1235, US1294, US1295, BG1764
> **Affects:** docs/release-notes-v6.5.0.md, tools/tests/test_lean_release_notes_v65.py, changelog.d/US1341.md
> **Epic:** EP0379
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering on 6.4.0 deciding whether her teams take 6.5 to the change board (Abena)
**I want** the 6.5 notes to describe what the widened release adds: a spend ceiling on a run,
an effort per kind of unit, the cache measures on the run report, the person's ownership of
the requirements documents, a committed record of each release with change failure rate
counted from it, and the disclosure line for a report signed under delegation before 6.5
**So that** the notes the board reads describe the release it approves, and a 6.4 team meets
the new refusals and keys in the notes before it meets them in a run

The operator widened 6.5 after its notes were written (D0635 to D0638). The notes name eight
themes and nothing run twenty-eight ships, and their cost section says runs sixteen to
twenty-six built 6.5, though runs twenty-seven and twenty-eight build it too. This story adds
four themes and widens a fifth. It names the three new refusals a 6.4 habit can meet and the
five configuration keys 6.5 now adds, and it corrects the cost section. Every statement is one
a feature story's criteria make true, and no figure is stated that a signed report does not
carry.

## Acceptance Criteria

### AC1: the lead names the cost controls the widened release adds

- **Given** docs/release-notes-v6.5.0.md once US1332 to US1338 and BG1764 are Done
- **When** the first section, 'What changed for you', is read
- **Then** it holds two more theme bullets, each naming exactly these units and no others.
  The first is "A run stops on spend as well as minutes and units, and effort can be set by
  kind of unit" (US1332, US1333, US1336). It says the spend appetite is counted in priced
  input-equivalent tokens and set by `appetite.spend`, `capacity.spend` or `--appetite-spend`,
  both keys shipping at 0, so no run has a spend ceiling until one is set. It says the breaker
  warns at 75 and 95 per cent and, at the appetite, starts no further unit while the units
  already dispatched finish. It says a meter that cannot read leaves spend unjudged at that
  boundary and says so, while minutes and units still stop the run. It says
  `sprint appetite resize --spend` raises the ceiling only with `--decision` naming a decision
  `sdlc-studio/decisions.md` records. And it says `routing.effort` takes `docs`, `bug` and
  `code` entries, shipped empty, which `sprint plan` stamps on each unit by its kind and
  `sprint lane brief` names. The second is "The run report shows where each role's cache spend
  went, against its earlier runs and the cache's lifetime" (US1334, US1335, US1337, US1338,
  BG1764). It says the report sets each role's cache-read share against its mean over the last
  five signed runs, reading not available where no earlier run measured it. It says the close
  names a role whose share fell more than ten points below that mean, and `retro.py validate`
  then needs the retro's `## Cost` section to name it. It says `sprint cost --anatomy` and the
  report split each role's cache writes into growth and re-writes after the 5-minute and
  1-hour lifetimes. And it says a reviewer recorded with its seat counts in the reviewer row,
  not under other. Fails on: the notes at HEAD, which name none of these eight units and no
  spend, appetite, cache or `routing.effort` (`grep -cE` and `grep -ciE` each print 0); and the
  existing lead check, which refuses a ninth theme as "not one of the eight" (run at grooming on
  a planted bullet).
- **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_lead_names_the_widened_cost_controls
- **Caller:** n/a: the subject is the page, the notes README links as the current release
  from the cut on

### AC2: the lead names ownership, the release record and the disclosure line

- **Given** the same notes once US1339, US1340, US1233, US1234, US1235, US1294 and US1295 are
  Done
- **When** the first section and the Sources table are read
- **Then** two more themes name exactly their units. The first is "The person owns the PRD and
  the PVD, and a seat checks the work against each under authority the person delegates"
  (US1339, US1340). It says the person owns every document the skill keeps, and the Product
  Owner or Product Manager seat signs its document's review leg, corrects a fact itself,
  proposes any change to a requirement, a priority or the scope as a change request the person
  decides, and asks the person when unsure. The second is "Each release leaves a committed
  record, and change failure rate is counted from those records" (US1233, US1234, US1235). It
  says the cut writes one record per version, naming its date and the reports signed since the
  previous release. It names the `escape.py` verb US1234 adds, read from its parser, which counts
  the releases with a linked incident over the releases counted in a window. It says a release
  inside the settling period is pending, and a project with no release or no incident record
  reads not measured, never 0%. And it says the sprint report and `retro.py seats` show the
  same figure beside the CI-run rate, which is unchanged. The existing delegated-signature theme
  also names US1294 and US1295. It names the `sprint_report.py` verb US1294 adds, read from its
  parser, which puts a disclosure line naming an accepted decision on a report already signed,
  after which the report still checks VALID. And it says RPT0029 to RPT0034 and the 6.4.0
  evidence pack now name the decision behind each delegated signature. The Sources table gains
  a row for each new theme, and the test's closed theme list is widened to the twelve. Fails
  on: the notes at HEAD, which name none of these seven units and no ownership, change failure
  rate, release record or disclosure for a report already signed (`grep -ciE` prints 0); and the
  delegated theme at HEAD, which names only US1290 to US1293.
- **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_lead_names_ownership_the_release_record_and_the_disclosure
- **Caller:** n/a: the subject is the page

### AC3: the new refusals a 6.4 habit meets are named beside what to do instead

- **Given** the 'Changed defaults and new refusals' section
- **When** it is read
- **Then** it gains three bullets, each with an `Instead:` clause. First, `sprint plan`
  refuses an unknown kind, role or effort under `routing.effort`, naming the key, with exit 2
  and nothing selected or written, where 6.4 planned and ignored the entry; instead, use a kind
  of `docs`, `bug` or `code` holding `builder` or `reviewer`, or remove the entry. Second,
  `retro.py validate` refuses a retro whose `## Cost` section does not name each role the close
  recorded as a cache-read fall, and a rolling boundary stops on a fall its retro does not
  name; instead, add a `## Cost` section naming each role the close named and the cause. Third,
  the report of record's annex moves to the version `sprint_report.EVIDENCE_SCHEMA_VERSION`
  holds, adding the conditional sections `cache_read_trend` and `cost_cache_writes`, which a
  page filed before them does not carry; instead, read both as conditional, as the annex lists
  them. The Breaking sentence still names every fragment filed under Breaking when the test
  runs. The test's closed list of changes is widened to the thirteen. Fails on: the section at
  HEAD, which names no `routing`, `cache-read`, `## Cost`, annex or `evidence_schema` (grep
  prints 0); and the existing check, which refuses a bullet no listed change names (run at
  grooming on a planted `routing.effort` bullet).
- **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_widened_release_names_its_new_refusals
- **Caller:** n/a: the subject is the page

### AC4: the upgrade path names the keys the widened release adds

- **Given** the 'Upgrading from 6.4' section and `reference-config.md` once US1332 and US1336
  are Done
- **When** its list of the keys 6.5 adds is read
- **Then** it also names `appetite.spend`, `capacity.spend`, `routing.effort.docs`,
  `routing.effort.bug` and `routing.effort.code`, each with the default `reference-config.md`
  states for it (0 for each spend key and an empty mapping for each kind, per D0637). It says
  the spend unit is priced input-equivalent tokens and a run with neither spend key set has no
  spend ceiling, and that an empty kind entry leaves every unit at its role's effort. The
  sentence saying `--apply` writes only `personas.standard` of these keys stays true, held by
  the existing step check, which runs the notes' steps on three 6.4 projects. The test's closed
  list of new keys is widened to the nine. Fails on: the section at HEAD, which names none of
  the five keys (`grep -cE` prints 0); and the existing check, which refuses `appetite.spend` as
  "a key 6.5 does not add" (run at grooming on a planted bullet).
- **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_upgrade_path_names_the_widened_keys
- **Caller:** `migrate.py`, whose dry run and `--apply` the section's steps run, unchanged by
  run twenty-eight's units

### AC5: the cost section names every run that built 6.5, and the count line stays

- **Given** the 'What the 6.5 runs cost' section and the notes as a whole
- **When** they are read
- **Then** the section's opening says runs sixteen to twenty-eight built 6.5. It says the table
  holds the reports of runs sixteen to twenty-six, and that runs twenty-seven and twenty-eight
  are reported in their own signed reports, with no figure given here. Every cost figure the
  notes state still names one of RPT0035 to RPT0045 and is read back from that report's JSON.
  The notes keep exactly one `**v6.5.0 discloses N open defects: N Medium, N Low.**` line, in
  digits, for `known_issues.py write --release 6.5.0` to fill. `tools/check_links.py` and
  `tools/lint-style.sh`, run on a tree holding the notes, pass. Fails on: the section at HEAD,
  whose line 196 reads "Runs sixteen to twenty-six built 6.5" and which names neither run
  twenty-seven nor run twenty-eight; and a figure cited from a report outside RPT0035 to
  RPT0045, which the existing figure check refuses.
- **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_cost_section_names_every_run_that_built_65
- **Caller:** `tools/known_issues.py write --release 6.5.0`, which fills the count line at the
  cut (`NOTES_TEMPLATE`)

## Notes

- Serves: Abena Osei, End goal 3, verbatim from her card: "Know what each team's delivery
  costs per point and hold it to a monthly budget, whichever harness a team uses" (the spend
  ceiling and the cache measures); End goal 2, "Every specification and every change names an
  accountable person, not 'the agent'" (ownership and the disclosure line); and End goal 1,
  "Every release passes the change board on the evidence the run produced, with no separate
  write-up" (the release record).
- The existing checks are closed lists, so each must be widened, not bypassed: `THEMES` (keep
  the quality theme first, since `quality_problems` reads `next(iter(THEMES))`), `CHANGES`
  and `NEW_KEYS`. Each was probed at grooming (Evidence N1): a ninth theme, a tenth-change
  bullet and an `appetite.spend` key bullet are each refused as they stand.
- Two pattern traps, both run at grooming (Evidence N1). `COST` reads "10 points" as a cost
  figure with no report named, so write "ten points". `OPEN_TALK` is case-insensitive, so a
  sentence holding the word "medium" (an effort level) or "bug" with "open" is read as
  open-defect talk, and any digit in it then needs a quality decision named. Keep effort level
  names and digits out of the same sentence.
- No unit id may appear outside a theme bullet except in the known-issues, sources and
  contributors passages, the Breaking sentence and BG1613 in the upgrade path (`lead_problems`).
  So the three new change bullets and the five keys name no unit.
- Read the new keys' defaults with `test_lean_specs_v64.config_defaults`, which reads the
  column headed Default: `reference-config.md`'s capacity table puts it second and its routing
  table third.
- The `escape.py` and `sprint_report.py` verbs, the release record's path and the settling
  period were not fixed at grooming (see "Read this first"). Read each verb from the script's
  parser when the test runs, never typed here.
- No cost figure for run twenty-seven or twenty-eight: at grooming no RPT0046 is filed, and run
  twenty-eight's report is signed after the cut. `RUNS_65` stays RPT0035 to RPT0045.
- `gate.py --release` executes every story's Verify at each cut, so find each section by name
  and keep each check true after a later release.
- Each test names its mutant first: the notes at HEAD `af477fc6d` must fail it.

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | product seat | Groomed for run twenty-eight under D0638 |
| 2026-11-26 | orchestrator | Names RPT0029 beside RPT0030 to RPT0034 (D0640) |
