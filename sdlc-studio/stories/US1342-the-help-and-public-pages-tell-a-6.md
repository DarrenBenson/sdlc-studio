# US1342: The help and public pages tell a 6.4 team how to cap a run's spend, answer a cache-read fall and read a release's change failure rate

> **Status:** Ready
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Depends on:** US1332, US1333, US1334, US1335, US1336, US1337, US1339, US1340, US1233, US1234, US1235, US1294, US1344, US1345, US1346, US1347, US1348
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/retro.md, .claude/skills/sdlc-studio/help/gate.md, README.md, docs/existing-users.md, docs/engineering-leaders.md, docs/enterprise.md, tools/tests/test_lean_docs_v65.py, changelog.d/US1342.md
> **Epic:** EP0379
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering reading the docs before her teams adopt 6.5 (Abena)
**I want** the help pages to say how to set a spend ceiling and an effort per kind of unit,
what a cache-read fall asks of a retro, and where a release's record and change failure rate
come from, and the public pages to say what the widened 6.5 adds and who owns the
requirements documents
**So that** no page sends my teams into a refusal it never mentioned, and the board reads one
account of what a run may spend and who owns each document

Run twenty-eight's feature stories document their keys in `reference-config.md` and their
behaviour in the reference pages, but four help pages and four public pages still describe 6.4
on these points. The engineering leaders page and the enterprise page say a run is capped only
by minutes and units, which US1332 makes false. help/sprint.md says the plan stamps one effort
on every unit, which US1336 makes false. help/retro.md lists what `retro validate` checks and
names no `## Cost` section, and help/gate.md and help/retro.md name no release record or change
failure rate. This story brings each page up to what shipped, without restating the reference
pages.

## Acceptance Criteria

### AC1: help/sprint.md names the spend ceiling and the effort by kind of unit

- **Given** help/sprint.md once US1332, US1333 and US1336 are Done
- **When** its 'Appetite: the circuit breaker' section and its Reasoning effort paragraph are
  read
- **Then** the Appetite section names the spend axis: `--appetite-spend` on `plan`, and
  `appetite.spend` and `capacity.spend`, counted in priced input-equivalent tokens, with 0
  meaning no spend ceiling. It names the warnings at 75 and 95 per cent. It says that at the
  appetite no further unit starts and units already dispatched finish. It says a meter that
  cannot read leaves spend unjudged at that boundary and says so, while minutes and units still
  stop the run. And it says `sprint appetite resize --spend N` raises the ceiling only with
  `--decision <id>` naming a decision `sdlc-studio/decisions.md` records. The Reasoning effort
  paragraph names the `docs`, `bug` and `code` entries under `routing.effort` and how a unit's
  kind is read: a bug by its id, else code when an Affects path is a code file, else docs. It
  says `sprint plan` refuses an unknown kind, role or effort, naming the key, and that the
  reviewer-below-builder rule holds within a kind. It says `sprint lane brief` names the unit's
  own effort, and that the entries ship empty. The exit code and the refusal the page names are
  checked against `loop_guard.py budget` and `sprint.py plan` run on fixtures. Fails on:
  help/sprint.md at HEAD, whose Appetite section names only `--appetite-minutes` and
  `--appetite-units` (line 462) and no spend (`grep -n` on the spend keys and `75 and 95` prints
  nothing), and whose Reasoning effort paragraph says the plan "stamps both on every unit"
  (line 327) and names no kind.
- **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_sprint_help_names_the_spend_ceiling_and_effort_by_kind
- **Caller:** n/a: the subject is the help page `/sdlc-studio sprint help` loads

### AC2: the help names the cache measures and what a retro then owes

- **Given** help/sprint.md and help/retro.md once US1334, US1335 and US1337 are Done
- **When** help/sprint.md's `cost --anatomy` paragraph and help/retro.md's `retro validate` row
  are read
- **Then** the anatomy paragraph says `cost --anatomy` splits each role's cache writes into
  growth and re-writes after 5-minute and 1-hour expiry, with a write's lifetime read from its
  kind and a role with an untimed record reading not available for its split. The validate row
  says a retro owes a `## Cost` section in two cases: when the close recorded a `cost` known
  issue, it names the cause; when the close recorded a `cache-read` one (a role whose cache-read
  share fell more than ten points below its mean over the last five signed runs), it names each
  such role. It also says a rolling boundary stops on a fall its retro does not name, linking
  `reference-sprint.md#cost-regression`. The refusal is checked against `retro.py validate` run
  on a fixture carrying a `cache-read` known issue and a retro with no `## Cost` section. Fails
  on: help/sprint.md at HEAD, which names no "re-writ" or "expiry" (its one "growth", line 400,
  is about an epic's priced set); and help/retro.md at HEAD, which holds no `## Cost` and no
  `cache-read` (`grep -c` prints 0).
- **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_help_names_the_cache_measures_and_the_retro_they_demand
- **Caller:** n/a: the subject is the help pages `/sdlc-studio sprint help` and
  `/sdlc-studio retro help` load

### AC3: the help names the release record, the change failure rate and the disclosure verb

- **Given** help/gate.md, help/retro.md and help/sprint.md once US1233, US1234, US1235 and US1294
  are Done
- **When** help/gate.md's release section, help/retro.md's `retro.py seats` paragraph and
  help/sprint.md's `sign` paragraph are read
- **Then** help/gate.md says the release cut writes one committed record per version, naming its
  date and the reports signed since the previous release, that a second cut of the same
  version leaves it unchanged, and where it is written, read from `release_cut.py`'s code in a
  fixture cut. help/retro.md says the seat scorecard states the release change failure rate
  with its source records, the figure the `escape.py` verb US1234 adds prints for the same
  window, pending inside the settling period and not measured, never 0%, with no release or
  incident record, linking help/deploy.md. help/sprint.md names the `sprint_report.py` verb
  US1294 adds. That verb puts a disclosure line naming an accepted decision on a report already
  signed, leaving its fingerprint and `sprint_report.py check`'s VALID unchanged. It refuses an
  unsigned report, or a decision `sdlc-studio/decisions.md` does not hold as accepted, writing
  nothing, and writes one line however often it runs. Each verb is read from its script's
  parser. Fails on: help/gate.md at HEAD, which holds no "release record" (`grep -ci` prints 0);
  help/retro.md at HEAD, which holds no "failure rate" (0); help/sprint.md at HEAD, whose `sign`
  paragraph covers only a signature entered with `--delegated --decision`; and the parsers at
  HEAD, where `escape.py` has only `trace` and `to-class` and `sprint_report.py` has no
  disclosure verb.
- **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_help_names_the_release_record_failure_rate_and_disclosure
- **Caller:** n/a: the subject is the help pages `/sdlc-studio gate help`,
  `/sdlc-studio retro help` and `/sdlc-studio sprint help` load

### AC4: the public pages say what the widened 6.5 adds and who owns the requirements

- **Given** README.md, docs/existing-users.md, docs/engineering-leaders.md and docs/enterprise.md
  once the feature stories are Done
- **When** each is read
- **Then** README's single 'New in 6.5' line also says a run can stop on spend, still within
  `test_readme_front_door`'s 1,500 words. existing-users.md's 'From 6.4 to 6.5' names
  `appetite.spend`, `capacity.spend`, `routing.effort.docs`, `routing.effort.bug` and
  `routing.effort.code` as optional keys, each with the default `reference-config.md` states for
  it, and has an item saying a retro must name in its `## Cost` section each role the close
  names as a cache-read fall. engineering-leaders.md's cost section says a run can be stopped
  on spend through `capacity.spend` or `appetite.spend`, in priced input-equivalent tokens, both
  at 0 and unbounded by default, and that the reading is a lower bound, so the stop can come
  late but never early. It still says there is no dollar budget setting. Its separation of
  duties section says the person owns the PRD and the PVD and the seat checks the work against
  each under authority the person delegates: it corrects a fact itself, proposes any change to
  a requirement as a change request the person decides, and asks when unsure. That sentence
  links the seats section US1339 renames. Its change approval section names the release change
  failure rate, counted from release records and linked incidents and never 0% unmeasured,
  linking `escape.py`. The page stays within 1,200 words, every claim links its mechanism, and
  no new sentence names an agent or accountability outside the page test's approved list.
  enterprise.md's cost section names `capacity.spend`, `appetite.spend` and `--appetite-spend`
  beside minutes and units, and its harness and models section names the per-kind
  `routing.effort` entries. Its command and key check stays green. `tools/check_links.py` and
  `tools/lint-style.sh` pass. Fails on: README's 6.5 line at HEAD, which names no spend
  (`grep -ciE` prints 0); existing-users.md at HEAD, which names none of the five keys (0);
  engineering-leaders.md at HEAD, whose line 110 says "A run is capped by wall-clock minutes and
  a number of units." and which names no change failure rate and no owner (0); and enterprise.md
  at HEAD, whose line 125 bounds a run by `capacity.minutes` and `capacity.units` alone and whose
  line 24 names only the builder's and reviewer's effort.
- **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_public_pages_name_what_the_widened_65_adds
- **Caller:** n/a: the subject is the public pages

### AC5: the upgrade page says how to turn on the solution review

- **Given** docs/existing-users.md once US1344 to US1348 are Done
- **When** its 'From 6.4 to 6.5' section is read
- **Then** its optional-keys item names `review.solution_review.min_points` and
  `review.solution_review.risk_classes`, each with the default `reference-config.md` states, and
  one new item says the solution review is off at those defaults, gives the lines that turn it
  on, says a risk class is read through `risk.components`, says `sprint lane land` refuses a
  named unit until a seat's GO stands on its approach note, names `critic.py approach brief` and
  `critic.py approach record` as their parser reads them, and links help/sprint.md's Lanes
  section for the rest, naming no unit or decision id. `NEW_KEYS` gains the two keys, and the
  turn-on lines, written to a fixture project's config, make `critic.solution_review_reason` give
  a reason for a 3-point story where the shipped defaults give None. Fails on: existing-users.md
  at HEAD `f946c5460`, which names no solution review and no `solution_review` key.
- **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_upgrade_page_says_how_to_turn_on_the_solution_review
- **Caller:** n/a: the subject is the upgrade page

## Notes

- Serves: Abena Osei, End goals 2 and 3 (quoted under story 1), and Maya Okafor (Secondary) on
  the upgrade path.
- Word budgets, measured at HEAD with `wc -w`. README.md is 1,496 of the 1,500 words
  `test_readme_front_door.py` allows (`CR0742_WORDS`), so the spend clause needs words found
  elsewhere in README. Keep every phrase test_lean_docs_v63, v64 and v65 read (US1328's Notes
  list them). engineering-leaders.md is 1,055 of `WORD_LIMIT` 1,200, so the three additions
  share about 145 words.
- engineering-leaders.md: `test_engineering_leaders_page.py` is a closed world for any
  sentence matching `\b(?:sub)?agent|\baccountab`, and that test is not in Affects. Write the
  new sentences without those words. Each claim in the four sections must link a mechanism (a
  script, a reference heading or a committed record), and the link to US1339's renamed seats
  section must resolve. Reuse that test's `claim_problems`, `word_count` and
  `signer_sentence_problems`, and `test_enterprise_doc.command_problems`, by import, as US1328's
  test reuses its neighbours.
- help/sprint.md is in US1333's Affects; US1333 adds the two appetite fields there. Build on
  what it wrote: if its Appetite section already names part of the spend axis, keep it and add
  only what is missing.
- Check each refusal against the shipped command on a fixture, as US1328 did. Reuse the feature
  stories' fixture helpers by import (`test_loop_guard_spend`, `test_effort_by_kind`,
  `test_cache_read_fall`) rather than building a second fixture. Keep each test under verify_ac's
  120-second bound: the module's four tests took 59 s together at grooming.
- No unit or decision id in a help or public page. `lint-style.sh` refuses a parenthetical
  `(CR`, `(BG` or `(RFC` id in help pages.
- Not in Affects: help/deploy.md (US1234 names the command there), help/pvd.md and the reference
  pages (US1339), help/arguments.md (US1333), docs/evidence.md (regenerated by the cut), and the
  README Version line and install pins (the cut's).

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | product seat | Groomed for run twenty-eight under D0638 |
| 2026-11-27 | product seat (D0545) | Adds AC5 and the EP0385 dependencies under D0652: the operator added the solution review to 6.5 (D0646) after this story was groomed, and the upgrade page would send a 6.4 team to a land refusal it never mentions. No EP0386 unit is added, since US1352 depends on this story; US1347 and US1352 document the rest in help/sprint.md |
