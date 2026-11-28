# SDLC Studio v6.5.0

**SDLC Studio 6.5.0 is the current release: it shipped only once its open defects met the bar
the operator set, and every persona and seat card is now held to a written standard before it
frames a brief.**

Every entry is in [the CHANGELOG's 6.5 section](../CHANGELOG.md#650---2026-11-28). From 6.4,
the "Upgrading from 6.4" section below is the whole path; from an earlier release, start with
[the existing-users page](existing-users.md).

## What changed for you

- **6.5 ships with fewer than 50 open defects and none at Medium or above (D0560).** The
  operator held this release to that bar and made the release wait for it. The reduction
  started from 473 open bugs after run twenty, 99 of them Medium (D0560). A qa-seat agent then
  re-checked every open bug at HEAD, and a closure was applied only when a second, independent
  engineering-seat agent failed to refute it (D0563). The operator approved two Won't Fix
  lists, each bug's ground and reason written into its Resolution: 139 Low bugs no user of the
  installed skill can meet (D0564), and 128 more Low bugs (D0613). The count this release ships
  with is the disclosure line under [Known issues](#known-issues), written at the cut.
- **Every persona and seat card is held to a written standard before it frames a brief, and
  the goal review says when nothing can check the goal.** A persona standard,
  `best-practices/persona.md`, names every rule a persona or seat card is held to, and
  `persona_review.py check` reports each card against it. `persona_review.py brief --card
  <card> --seat <seat>` briefs a seat other than the card's own to review it,
  `persona_review.py record` keeps its dated verdict, and `persona_review.py owed` names each
  card owed a review. A project seat card that breaks a blocking rule, or whose latest review
  failed, frames no brief: `persona_resolve.py resolve` and the briefs that call it refuse it,
  naming each rule and the command to run next, and `personas.standard: report` frames it with
  a warning instead. `validate.py seats` warns on a seat card naming a persona the cast does not
  declare, and `persona_review.py check` finds nothing that blocks on the three shipped amigo
  cards copied verbatim. `sprint.py goal-review brief --seat <role>` briefs one review seat
  through its own card, lists the End goals of each persona the Sprint Goal traces to, and
  prints a `Goal check: NONE - nothing can check this goal` line when none of them carries an
  executable Verify; `sprint plan` prints the same reading as its `goal check:` line. A shipped lesson tells an
  orchestrator to brief every agent it spawns with the render of the seat whose lens fits the
  work. Delivered by US1036, US1039, US1040, US1046, US1052, US1053, US1054, US1055, US1056,
  US1057, US1322 and CR0748.
- **A sprint walks a wave from build to paperwork and wakes the model only at a refusal, a
  warning, a REJECT, a rebase conflict or the wave's end, and the author's own mutants reach the
  reviewer replayed.** `sprint.py drive --harness <cli>` walks a unit's lane from the headless
  build through `lane land`, the review, `lane accept` and one paperwork commit with no model
  between its steps, and drives the open run's current wave in parallel, units with disjoint
  Affects at once. It stops with a decision record naming the unit, the step and the command
  that resumes. `sprint.py drive step --after <agent-id>` runs the whole chain after one
  agent's hand-back and ends with the next prompt's path. `sprint lane land` lands several
  builders' worktrees as one commit, `sprint lane land --resume` takes up a landing that
  stopped, and `sprint.py lane brief --repair` quotes a refused landing and a REJECT's findings
  byte for byte. `mutation.py run --edits <list.json> --scope <id>` runs the mutants an author
  chose in a copy of the tree, `critic.py self-check record --mutants-from <report>` records
  its report, and `critic.py brief` replays that list against the tree as it stands, marking a
  mutant whose verdict has changed. Delivered by US1192, US1193, US1195, US1196, US1197,
  US1198, US1200, US1201 and US1202.
- **A delegated signature names the decision that authorised it, and a run awaiting its
  signature no longer holds up the next.** `sprint sign --delegated --decision <id>` records
  `delegated: true` and the accepted decision that authorised the signature; the report page's
  Signed by cell and the evidence pack's Accountable lines name both, and the pack refuses a
  report whose signature drops a delegation its run record holds. A run closed and awaiting
  its signature no longer holds the run slot: `sprint plan --write` names each waiting run and
  opens the next, and `sprint sign` seals the waiting run later, judged against the commit that
  filed its record once HEAD has moved past it. `sprint_report.py disclose` puts a disclosure
  line naming an accepted decision on a report already signed, after which the report still
  checks VALID, and RPT0029 to RPT0034 and the 6.4.0 evidence pack now name the decision behind
  each delegated signature. Delivered by US1290, US1291, US1292, US1293, US1294 and US1295.
- **A configuration a project switched on is never read as off, because PyYAML is required.**
  Without PyYAML a project's `.config.yaml` was read as the shipped defaults with one warning,
  so a gate the project switched on was off. Now `install.sh` and `install.ps1` refuse a
  machine whose Python cannot import PyYAML, a command that reads a present `.config.yaml`
  exits 1 naming `python3 -m pip install pyyaml`, and `gate.py` exits 2 before any lane starts.
  Delivered by US1296, US1297, US1298 and US1299.
- **A red CI run on main is answered by a written policy.** After a `trunk` push, the shipped
  guidance waits on the CI run with one blocking command under a timeout, `timeout 30m gh run
  watch <id> --exit-status`, never a polling loop, and reads a red main before pushing again.
  `gate.py --red-run <run> --failed <test> --token can-rerun` answers a red run: `rerun` when
  every failing test is named by an open flaky bug and the run's reds are fewer than
  `ci.rerun_limit`, `stop` past that limit or with a token that cannot rerun, and `regression`
  when any failing test is named by no open flaky bug. Delivered by US1236, US1237 and US1238.
- **SDLC Studio is documented as a harness-agnostic Agent Skill.** [The harness
  page](harnesses.md) shows what SDLC Studio gives in Claude Code, Codex, Cursor, Gemini CLI,
  GitHub Copilot and opencode, each cell naming the file that shows it or opening with
  Untested, and what a harness without a feature does instead. [The enterprise
  page](enterprise.md) answers an enterprise reviewer on harness and models, data, adopting
  without forking, existing controls, cost and verification, and names every file in the
  installers and the installed skill that makes a network call. The README's first screen, the
  `SKILL.md` compatibility line, `llms.txt` and `package.json` no longer name Claude Code as
  required, and [the evidence page](evidence.md) gains a Model column. Delivered by US1315,
  US1316, US1317, US1318, US1319, US1320 and US1321.
- **Filing and planning catch overlap before a run pays for it.** `file_finding.py file`
  refuses a finding that shares every declared `Affects` path with an artefact of its type and
  whose title the duplicate lens scores at or above its bar, with exit 1 and nothing written,
  unless `--distinct-from <id>` rules it distinct. `sprint plan` names, per unit, the test
  modules outside its `Affects` that name a `.py` file it declares. `reconcile.py detect`
  reports a story whose stamped `Risk-class` ranks below the class the component map now gives
  its `Affects`, and `reconcile.py apply` raises it and never lowers one. Delivered by US1314,
  US1324 and US1326.
- **A run stops on spend as well as minutes and units, and effort can be set by kind of unit.**
  The spend appetite is counted in priced input-equivalent tokens and set by `appetite.spend`,
  `capacity.spend` or `--appetite-spend`, both keys shipping at 0, so no run has a spend ceiling
  until one is set. The breaker warns at 75 and 95 per cent and, at the appetite, starts no
  further unit while the units already dispatched finish. A meter that cannot read leaves spend
  unjudged at that boundary and says so, while minutes and units still stop the run. `sprint
  appetite resize --spend` raises the ceiling only with `--decision` naming a decision
  `sdlc-studio/decisions.md` records. `routing.effort` takes `docs`, `bug` and `code` entries,
  shipped empty, which `sprint plan` stamps on each unit by its kind and `sprint lane brief`
  names. Delivered by US1332, US1333 and US1336.
- **The run report shows where each role's cache spend went, against its earlier runs and the
  cache's lifetime.** The report sets each role's cache-read share against its mean over the
  last five signed runs, reading not available where no earlier run measured it. The close
  names a role whose share fell more than ten points below that mean, and `retro.py validate`
  then needs the retro's `## Cost` section to name it. `sprint cost --anatomy` and the report
  split each role's cache writes into growth and re-writes after the 5-minute and 1-hour
  lifetimes. A reviewer recorded with its seat counts in the reviewer row, not under other.
  Delivered by US1334, US1335, US1337, US1338 and BG1764.
- **The person owns the PRD and the PVD, and a seat checks the work against each under
  authority the person delegates.** The skill says the person owns every document it keeps,
  and the Product Owner or Product Manager seat signs its document's review leg, corrects a fact
  itself, proposes any change to a requirement, a priority or the scope as a change request the
  person decides, and asks the person when unsure. Delivered by US1339 and US1340.
- **Each release leaves a committed record, and change failure rate is counted from those
  records.** The cut writes one record per version to `sdlc-studio/reports/releases.jsonl`,
  naming its date and the reports signed since the previous release. `escape.py failure-rate`
  counts the releases with a linked incident over the releases counted in a window. A release
  inside the settling period is pending, and a project with no release or no incident record
  reads not measured, never 0%. The sprint report and `retro.py seats` show the same figure
  beside the CI-run rate, which is unchanged. Delivered by US1233, US1234 and US1235.
- **A builder's approach can be reviewed before any code is written.** A seat reviews the
  builder's approach note before any code is written. The step ships off, with
  `review.solution_review.min_points` at 0 and `review.solution_review.risk_classes` empty, and
  `min_points: 3` or `risk_classes: [high]` under `review.solution_review` turns it on. A third
  line there, `panel: [qa, product, persona]`, seats each named seat as its own review, and the
  approach is then agreed only when every seat has a GO on the note as it stands; the seat that
  builds a unit is skipped for it, as is `persona` for a unit whose story names no Persona.
  `critic.py approach brief` prints a seat's review brief for the note, `critic.py approach
  record` records its GO or CHANGES against the note's digest, `critic.py approach panel`
  prints one brief command, one reply file and one spend command for each seat, and
  `critic.py approach spend` adds a seat agent's priced spend to the unit's delegated spend in
  the open run. `sprint lane land` refuses a named unit until a GO stands on the note as it is,
  from every seat when a panel is set. The code review brief carries none of the note.
  Delivered by US1344, US1345, US1346, US1347, US1348, US1349, US1350, US1351, US1352,
  US1353 and BG1768.

## Changed defaults and new refusals

No 6.5 fragment is filed under Removed or Security. Filed under Breaking: US1299 and BG1063.
These are the changes a 6.4 habit meets as a new refusal or a changed default, each with what
to do instead:

- **PyYAML is required.** `install.sh` and `install.ps1` refuse a machine whose Python cannot
  import it, before any download. A command that reads a present `.config.yaml` exits 1 with
  one line naming `python3 -m pip install pyyaml`, where 6.4 read the shipped defaults, and
  `gate.py` exits 2 before any lane, whether or not the project has a `.config.yaml`.
  Instead: run `python3 -m pip install pyyaml` before installing or upgrading the skill.
- **`require_ac_verification` is retired.** No script ever read it, so setting it changed
  nothing, and `migrate --apply` removes it from `.config.yaml`.
  Instead: rely on `quality.done_requires_verified`, the Done gate `transition.py` reads, which
  is on by default.
- **A project seat card that breaks the persona standard frames no brief.** Under
  `personas.standard: block`, the default, a card that breaks a blocking rule of the standard,
  or whose latest persona review failed, is refused at every entry point that resolves it:
  `persona_resolve.py resolve` exits 1, and `critic.py brief` and the other briefs exit 2, each
  naming the card, every rule it breaks and the `persona_review.py brief --card <card> --seat
  <seat>` to run next. No other card stands in for it. `migrate --apply` sets
  `personas.standard: report` for a project holding its own persona or seat cards with no value
  set, so such a project is warned on stderr rather than refused.
  Instead: run `persona_review.py check` to list the cards a blocking rule holds, fix each
  named line or run the command each refusal prints, then set `personas.standard: block`.
- **`sprint sign --delegated` needs `--decision`.** The decision must be an accepted one in
  `sdlc-studio/decisions.md`; none, an unknown id or a superseded one is refused before
  anything is written, and `--decision` without `--delegated` is refused.
  Instead: sign as the operator with neither flag, or pass `--delegated --decision <id>` naming
  the decision that authorised the delegate.
- **`file_finding.py file` refuses a duplicate.** A finding that shares every declared `Affects`
  path with an artefact of its type, open or terminal, and whose title the duplicate lens
  scores at or above its bar exits 1 with nothing written, also under `--dry-run`, naming the
  existing artefact.
  Instead: read the artefact it names, and if the finding is a different one, file it with
  `--distinct-from <id>`.
- **`transition.py set --status Done` refuses a Draft or Proposed story that misses the
  Definition of Ready.** It names each unmet item: no `Affects`, an `Affects` none of whose
  paths resolve while one is a typo for a file elsewhere, or no `Points` on the scale.
  Instead: give the story its `Affects` and `Points`, or record a `> **Decision-Override:**
  <reason>` on it.
- **A run awaiting its signature no longer holds the run slot.** `sprint plan --write` names
  each waiting run and opens the next one, where 6.4 refused; a run open and not yet closed
  still refuses a disjoint batch.
  Instead: open the next run when it is ready, and sign the waiting run with `sprint sign`
  when its report is read.
- **An RFC gains a Delivered status.** Accepted is the decided state, and `reconcile apply`
  and a sprint close move an Accepted RFC to Delivered once every request or epic it produced
  is resolved.
  Instead: read Delivered, not Accepted, as an RFC whose work has shipped, and have a tool that
  reads RFC statuses accept the new value.
- **`reconcile.py apply` raises a story's stamped `Risk-class`.** An open story whose stamp
  ranks below the class the component map gives its `Affects` is raised to the map's class, and
  a stamp is never lowered.
  Instead: change the component map to change the class a story reads at, or raise a stamp by
  hand for a story that needs a higher class than the map gives.
- **`sprint plan` refuses an unknown `routing.effort` entry.** An unknown kind, role or effort
  under `routing.effort` exits 2 naming the key, with nothing selected or written, where 6.4
  planned and ignored the entry.
  Instead: use a kind of `docs`, `bug` or `code` holding `builder` or `reviewer`, or remove the
  entry.
- **`retro.py validate` refuses a retro that leaves a cache-read fall unnamed.** A retro whose
  `## Cost` section does not name each role the close recorded as a cache-read fall is refused,
  naming the role, its share and its mean.
  Instead: add a `## Cost` section naming each role the close named and the cause.
- **The report of record's annex moves to version 1.1.** It adds the conditional sections
  `cache_read_trend` and `cost_cache_writes`, which a page filed before them does not carry.
  Instead: read both as conditional, as the annex lists them.
- **A high-class unit's second review seat is product on the shipped seats.** `sprint plan`
  gave every high-class unit engineering, the default building seat, as its second review
  seat, so that review was the builder's own.
  Instead: brief the second seat the plan names with `critic.py brief --seat <seat>`.

## Upgrading from 6.4

Install PyYAML, reinstall, then carry each project across:

```bash
python3 -m pip install pyyaml
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: lists what it would change, writes nothing
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # writes what the dry run listed, and nothing else
```

**PyYAML first.** 6.5 refuses to install on a machine whose Python cannot import PyYAML, so
install it with `python3 -m pip install pyyaml` before reinstalling.

**Reinstall.** A plain `install.sh` or `install.ps1` fetches the latest published release; pass
`main` as the version for the moving branch.

**`migrate`** is the dry run: it writes nothing. For a 6.4 project it lists the version stamp
(`sdlc-studio/.version stale (skill 6.4.0 -> 6.5.0)`); for a project holding its own persona
or seat cards, also `set personas.standard: report`; and for one carrying
`require_ac_verification`, that key's removal (`require_ac_verification removed`). Beside them
it lists anything it leaves to you, such as a seat role with no card.

**`migrate --apply`** writes exactly what the dry run listed: the stamp to
`sdlc-studio/.version` and, where listed, `personas.standard: report` into `.config.yaml` and
`require_ac_verification` out of it, and changes nothing else. Of the keys below it writes only
that `personas.standard`, so a project reads each other key at its default until it sets it.

6.5 adds these configuration keys:

- `personas.standard`, default `block`: how the persona standard holds the project's own
  cards; `report` frames a card that breaks it and prints one warning line.
- `ci.wait_timeout_minutes`, default `30`: documented as the limit on the one blocking watch of
  a push's CI run, but no script in 6.5.0 reads it (BG1613).
- `ci.rerun_limit`, default `1`: the reruns one red run may have when every failing test is a
  filed flaky bug, which `gate.py --red-run` reads.
- `review.rendered_paths`, default `[]`: globs of the files the project's build consumes, which
  `critic.py caller-check` reads as no mechanism.
- `appetite.spend` and `capacity.spend`, default `0`: the run's spend ceiling, counted in priced
  input-equivalent tokens; `appetite.spend` at 0 inherits `capacity.spend`, so a run with
  neither spend key set has no spend ceiling.
- `routing.effort.docs`, `routing.effort.bug` and `routing.effort.code`, default `{}`: the
  effort each role is spawned at for that kind of unit; an empty kind entry leaves every unit
  at its role's effort.
- `review.solution_review.min_points`, default `0`: a unit of this many points or more takes a
  solution review, so at 0 none does by points.
- `review.solution_review.risk_classes`, default `[]`: the risk classes whose units take a
  solution review whatever their points.
- `review.solution_review.panel`, default `[]`: the seats that review a unit's approach note,
  each its own agent; empty means one seat's GO agrees the approach.

## What the 6.5 runs cost

Runs sixteen to twenty-eight built 6.5. The table holds the reports of runs sixteen to
twenty-six, each signed by the operator's delegate under a decision of record and each row read
from that report's Estimates table. Runs twenty-seven and twenty-eight are reported in their
own signed reports, and no figure for them is given here. A total across reports is carried by
no single report, so none is given.

| Report | Run | Delivered | Dollar cost | Per point | Forecast per point |
| --- | --- | --- | --- | --- | --- |
| RPT0035 | sixteen | 51 points | $102.01 | $2.00 | $3.37 |
| RPT0036 | seventeen | 25 points | $54.60 | $2.18 | $3.18 |
| RPT0037 | eighteen | 48 points | $126.81 | $2.64 | $3.05 |
| RPT0038 | nineteen | 68 points | $139.29 | $2.05 | $3.05 |
| RPT0039 | twenty | 58 points | $167.06 | $2.88 | $3.05 |
| RPT0040 | twenty-one | 79 points | $288.42 | $3.65 | $3.20 |
| RPT0041 | twenty-two | 66 points | $316.41 | $4.79 | $3.86 |
| RPT0042 | twenty-three | 80 points | $333.81 | $4.17 | $4.25 |
| RPT0043 | twenty-four | 64 points | $187.89 | $2.94 | $5.46 |
| RPT0044 | twenty-five | 55 points | $161.82 | $2.94 | $5.46 |
| RPT0045 | twenty-six | 77 points | $362.06 | $4.70 | $5.46 |

## Known issues

Every open finding this release ships is listed by id on [the disclosure page](known-issues.md),
which `tools/known_issues.py write` generates from the bug corpus at the cut, together with the
count below, so the two cannot disagree.

**v6.5.0 discloses 49 open defects: 0 Medium, 49 Low.**

## For contributors to this repository

This repository's own tooling, which does not ship, changed too: `tools/remote-gate.sh staged`
runs only the named test modules on the gate host, and the commit-msg hook sends a commit's
selected modules there, running them on this machine only when the host gives no verdict; and
this repository declares its own component map under `risk.components`, so a change to a gate
script reads as high in review. Delivered by US1190, US1191 and US1313.

## Sources

Unit ids behind each passage, in this repository.

| Passage | Ids |
| --- | --- |
| Figures | RPT0035 to RPT0045 (`sdlc-studio/reports/`), each report's Estimates table |
| 6.5 ships with fewer than 50 open defects | D0560, D0563, D0564 and D0613 (`sdlc-studio/decisions.md`) |
| Every persona and seat card is held to a written standard | US1036, US1039, US1040, US1046, US1052, US1053, US1054, US1055, US1056, US1057, US1322, CR0748, BG1655 |
| A sprint walks a wave from build to paperwork | US1192, US1193, US1195, US1196, US1197, US1198, US1200, US1201, US1202 |
| A delegated signature names its decision | US1290, US1291, US1292, US1293, US1294, US1295 |
| PyYAML is required | US1296, US1297, US1298, US1299 |
| A red CI run on main | US1236, US1237, US1238 |
| A harness-agnostic Agent Skill | US1315, US1316, US1317, US1318, US1319, US1320, US1321 |
| Filing and planning catch overlap | US1314, US1324, US1326 |
| A run stops on spend | US1332, US1333, US1336 |
| Where each role's cache spend went | US1334, US1335, US1337, US1338, BG1764 |
| The person owns the PRD and the PVD | US1339, US1340 |
| Each release leaves a committed record | US1233, US1234, US1235 |
| A builder's approach can be reviewed | US1344, US1345, US1346, US1347, US1348, US1349, US1350, US1351, US1352, US1353, BG1768 |
| Changed defaults and new refusals | US1296, US1297, US1298, US1299, BG1063, US1055, US1056, US1322, US1291, US1324, BG0954, US1290, BG1569, US1314, BG1609, US1336, US1335, US1334, US1338 |
| Upgrading from 6.4 | US1299, US1322, BG1063, US1237, BG1606, BG1613, US1332, US1336, US1344 |
