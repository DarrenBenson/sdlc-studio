# SDLC Studio v6.2.0

**SDLC Studio 6.2.0 is the current release: a review brief can now require the author's own
check first, and a run states what it cost, priced over the main thread and every subagent.**

Every entry is in [the CHANGELOG's 6.2 section](../CHANGELOG.md#unreleased). From 6.1, the
"Upgrading from 6.1" section below is the whole path; from an earlier release, start with
[the existing-users page](existing-users.md).

## What changed for you

- **A reviewer judges only work its author has self-checked.** `critic.py brief` prints an
  author self-check on stderr: the claims to inventory (the commit message, each prose surface
  the brief names, each changelog fragment the unit declares) and the test files to mutate.
  `critic.py self-check record` writes that pass to `sdlc-studio/reviews/author-self-checks.md`,
  and refuses a claim ruled FALSE, a claims file with no claim, and a mutant that survived with
  no answer. The new `review.author_self_check` key decides what a brief does for a unit with no
  record matching its Affects as they stand: `report`, the shipped default, briefs and names the
  gap, and `block` refuses the brief. The brief also carries what a reviewer spent turns
  finding: the one command that runs the unit's Verify lines and, when a run names the unit,
  its diff from the run's base. Delivered by US1087, US1088, US1089 and US1094.
- **One command gives a builder its whole brief.** `sprint.py lane brief --units <id>` lists the
  unit's Affects, names the engineering seat card to adopt, prints the author self-check, and
  ends with the commands that run the unit's criteria (`verify_ac.py run --id <id>`), record the
  self-check, and stage exactly its Affects for the commit. The toolchain runbook's delivery
  table hands that brief to a fresh agent and accepts its work with
  `sprint.py lane return --units <id>`, rather than reading the builder's diff or transcript
  into the orchestrating context. Delivered by US1093.
- **A run states what it cost, priced, over the main thread and every subagent.** The token
  meter reads every subagent transcript a session ran beside the main thread, counts each
  assistant message once, and prices each reading, weighing input, output, cache writes and
  cache reads from one table. The sprint report's Estimates lead with a `Priced cost` row:
  RPT0023, the report of the last run before this release, prices it at 111,425,278 input-equivalent tokens over 69
  delivered points, where its input + output + cache-write sum is 23,269,314.
  `retro.py accuracy --tokens-from-harness` puts the same figure in the retro, VELOCITY.md gains
  a `Priced/pt` column, and `sprint.py close` compares the run's priced cost per point with a
  baseline. A run whose readings an earlier meter took is re-derived from its transcripts on the
  current basis, or reads not attributable, never a difference across two bases. Delivered by
  US1091, US1092, US1095 and US1097.
- **The gates cost less.** The conformance and engagement-floor lanes read the verdict ledger
  and the decisions log at most once each in a gate run, where they re-read both for every
  unit: judged over this repository's workspace, they opened the decisions log 2,256 times and
  the ledger 2,478 times, as BG1109's changelog entry records. At a push or a tag the gate's cost
  line judges only the standard lanes against its budget, naming the full suite and the release
  lanes beside it with their seconds, so a push is no longer reported over budget for running
  its suite; the budget is derived from the run `GATE_BUDGET_MEASURED` records in `gate.py`.
  Delivered by BG1065 and BG1109.

## Changed defaults and new refusals

No 6.2 fragment is filed under Breaking or Removed. These are the changes a 6.1 habit meets as a
new refusal or a changed default, each with what to do instead:

- **`critic.py brief` can refuse an unchecked unit.** The new `review.author_self_check` key
  ships as `report`, which briefs and names a missing record on stderr. Set to `block`, the
  brief exits 2 and prints nothing on stdout until
  `critic.py self-check record --unit <id> --claims <file> --mutants <file>` has recorded a
  self-check matching the unit's Affects as they stand. A value other than `off`, `report` or
  `block` refuses the brief, naming the value.
  Instead: record the self-check before you brief, or keep `report` until your builders do.
- **An amended Sprint Goal takes one goal-review round.**
  `sprint.py goal-review record --amend-from` carries every seat's verdict forward to the new
  wording, where 6.1 carried only the requesting seat's. A `--fields-file` `rereview` other than yes or no is refused, and so is
  an amended goal over twenty words. Instead: a seat that wants to judge the new wording answers
  `rereview: yes`, as a `--fields-file` key or a last `--seat` field, and `sprint.py plan` names
  it as owing a verdict; record a `--material` change to have every seat judge it afresh.
- **A close can file a cost known issue that the retro must answer.** `sprint.py close`
  compares the run's priced cost per point with the median of the five most recent priced runs
  once three exist, else with `cost.baseline_per_point`, shipped as `2500000`. A run more than
  one and a half times its baseline is recorded as a `cost` known issue, and `retro.py validate`
  refuses that run's retro until a `## Cost` section holds a bullet. Instead: write the cause
  under `## Cost`, and set `cost.baseline_per_point` to your own figure, or to `off` to leave the
  comparison unmeasured until three runs are priced.
- **The light review tier carries less.** `critic.py brief --tier light` no longer carries the
  files' history or the two mutation practices. Both tiers now carry the unit's Verify command
  and, when a run names the unit, its diff, cut at `review.brief_diff_lines` (`full: 400`,
  `light: 150`). Instead: brief at `--tier full` for a unit that needs its history or a mutation
  pass, and raise `review.brief_diff_lines` in `.config.yaml` for a longer diff.
- **The project lessons log is committed.** It lives at `sdlc-studio/retros/LESSONS.md`, where
  6.1 kept it in the gitignored `sdlc-studio/.local/lessons.md`. The first `lessons` command
  moves a legacy log there and says to commit it; with both files present it refuses, naming
  them. Instead: commit the moved log, and merge two machines' logs by hand when it names both.
- **`lessons.py revalidate --extend` needs a reason.** With no `--reason`, or a blank one, it is
  refused and writes nothing. Instead: pass `--reason` saying why the lesson still holds; it is
  recorded as the lesson's `Revalidated` line.
- **A closed run awaits its signature in every checkout.** `sprint.py close` files the run's
  record at `sdlc-studio/reports/runs/<RUN-ID>.json`, and `sprint.py plan --write` in a clone
  that does not hold the run open refuses while that record awaits a signature, naming the run,
  its report and the `sign` command. Instead: commit the record with the report, and sign from
  any clone with `sprint.py sign --report <id>`.
- **`sprint.py sign` re-derives the page before it seals.** It refuses a page that no longer
  re-derives to what the close filed, naming each figure that moved. A ruling logged with
  `decisions.py add` between the close and the sign is left out of the run's count, but it
  changes the tracked decisions log, so sign refuses until the run is re-closed. Instead: log
  rulings before `sprint.py close`; after a late one, commit it and run `sprint.py close` again
  before you sign.
- **`sprint.py sign` leaves a ruled carried unit where it is.** A batch unit the close's retro
  lists under `## Known issues carried` with a valid ruling is no longer moved to Done or Fixed,
  and sign names it as carried. Instead: take it up in a later run; to change it after the
  seal, `sprint.py reopen` the run first.
- **A builder's supplied token total is not added on top.** Where the run's readings hold the
  subagent transcripts, a total given with `sprint.py lane return --tokens N` is kept on the
  record but not added to the run's actual, since the meter already reads the builder's
  transcript. Instead: rely on the meter; a session that writes no subagent transcript reads the main thread alone and says
  the reading is a lower bound.
- **Token figures are on a new basis.** The meter counts each assistant message once, where 6.1
  summed every record the harness repeats for one, and it adds the subagent transcripts.
  VELOCITY.md rows written before are not re-derived. Instead: compare runs on the new
  `Priced/pt` column, which reads `-` on the rows written before it.
- **A story minted with no `--persona` follows its Affects** in a project that lists two or
  more Primaries: `artifact.py new --type story` and `batch` name the Primary whose card's
  `Interface` row holds all of the Affects' paths, else the first Primary the persona index
  lists. A project with one Primary mints as before.
  Instead: pass `--persona` to choose.
- **`doc_freshness.py --format json` gives `census` as a list**, one entry per document, now that
  it reads the PRD and the TSD beside the TRD. Instead: read each document's entry from the list.

## Upgrading from 6.1

Reinstall, then carry each project across:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: lists what it would change, writes nothing
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # restamps the project version, and nothing else
```

**Reinstall.** A plain `install.sh` or `install.ps1` fetches the latest published release; pass
`main` as the version for the moving branch.

**`migrate`** is the dry run: it writes nothing. For a 6.1 project it reports one deterministic
upgrade, the version stamp (`sdlc-studio/.version stale (skill 6.1.0 -> 6.2.0)`), beside
anything it leaves to you, such as a seat role with no card.

**`migrate --apply`** writes that stamp to `sdlc-studio/.version` and changes nothing else: no
6.2 fragment retires a config key or a command, so there is nothing for it to remove. The new
keys, `review.author_self_check`, `review.brief_diff_lines` and `cost.baseline_per_point`, are
not written to your `.config.yaml`; each reads its shipped default until you set it.

**Two records to commit.** `migrate` leaves a legacy `sdlc-studio/.local/lessons.md` where it
is: the first `lessons` command moves it to `sdlc-studio/retros/LESSONS.md` and says to commit
it. From the first 6.2 close, each run's record is filed under `sdlc-studio/reports/runs/`
beside its report: commit both.

## Known issues

Every open finding this release ships is listed by id on [the disclosure page](known-issues.md),
which `tools/known_issues.py write` generates from the bug corpus at the cut, together with the
count below, so the two cannot disagree.

**v6.2.0 discloses 174 open defects: 56 Medium, 118 Low.**

## For contributors to this repository

This repository's own tooling, which does not ship, changed too: the pre-push gate can run on a
gate host (`git config sdlc.gateHost <host>`), `tools/enable-hooks.sh` names each missing gate
prerequisite with its install route, the pre-push hook refuses a push that lacks one the suite
needs, and the PRD, TRD and TSD were refreshed against the code. The CHANGELOG lists each change.

## Sources

Unit ids behind each passage, in this repository.

| Passage | Ids |
| --- | --- |
| Figures | RPT0023 (`sdlc-studio/reports/`), its Estimates table; BG1109's changelog entry; `GATE_BUDGET_MEASURED` in `gate.py` |
| A reviewer judges only work its author has self-checked | US1087, US1088, US1089, US1094, BG1117 |
| One command gives a builder its whole brief | US1093 |
| A run states what it cost | US1091, US1092, US1095, US1097, BG1111, BG1127 |
| The gates cost less | BG1065, BG1109 |
| Changed defaults and new refusals | US1089, US1096, US1095, US1094, BG0989, BG1139, BG0993, BG0940, BG1025, US1091, BG1111, US1092, US1080, US1098 |
| Upgrading from 6.1 | BG0989, BG0993 |
| For contributors | US1003, US1005, US1075, US1076, US1077, US1078, US1084, US1085, US1086, US1099, US1100, US1101, US1102, US1103, US1104 |
