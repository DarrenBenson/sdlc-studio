# SDLC Studio v6.4.0

**SDLC Studio 6.4.0 is the current release: a release now carries the evidence a change board
accepts, and a run's cost is forecast before it starts and set beside what it cost.**

Every entry is in [the CHANGELOG's 6.4 section](../CHANGELOG.md#640---2026-11-16). From 6.3, the
"Upgrading from 6.3" section below is the whole path; from an earlier release, start with
[the existing-users page](existing-users.md).

## What changed for you

- **A release carries evidence a change board accepts.** `release_cut.py evidence-pack
  --version X.Y.Z --reports <ids>` writes a release's evidence pack from the signed reports it
  names, read as committed: each delivered change with its title, its ticked criteria and their
  Verify lines, the latest verdict of each seat whose reviewer is not its author, the known
  issues that name it, and the person who signed its report as the one accountable for it. An
  unsigned or unknown report, or a signer who reads as an agent, refuses the pack and nothing is
  written. The JSON page `sprint close` files, the committed run record and the ledgers are
  contracted in a versioned annex, `reference-evidence-schema.md`, which shows how to recompute
  a report's fingerprint with the Python standard library alone, and each page and run record
  states the annex version it was written under. A report cites the run record committed beside
  it, `sdlc-studio/reports/runs/<RUN-ID>.json`, which names the plan the run opened from by its
  digest, so the page reads the same in a teammate's clone. `sprint_report.py evidence --out
  <page>` writes the signed reports of record as one table, a row per run, and
  [the evidence page](evidence.md) lists this repository's own runs from it. Delivered by
  US0992, US0993, US0994, US0995, US0996, US0997, US0998, US1155, US1156, US1160 and US1161.
- **A run's cost is forecast before it starts and set beside the actual, priced at each model's
  own rate.** `sprint plan` prints a Minutes, Wall-clock span, Priced cost and Dollar cost
  forecast for the batch and `sprint plan --write` records each per unit, and the sprint
  report's Estimates table sets forecast, actual and their ratio side by side on the cost and
  span rows. A row with no measured rate reads `not forecast: <reason>`, never a guess.
  RPT0028, the report of the first run that built 6.4, recorded $126.64 over 51 delivered
  points, $2.48 a point, with no forecast to set beside it. RPT0032 forecast $182.64 and
  recorded $126.86 over 54 delivered points, $2.35 a point against a forecast of $3.38.
  RPT0033 forecast $169.11 and recorded $108.81 over 50 delivered points, $2.18 a point against
  a forecast of $3.38. The price table now prices xAI Grok, Cursor Composer and Copilot's token
  billing in AI credits, `pricing.copilot_billing` bills a Copilot run on its plan's one basis,
  and the report's appendix lists the price each model's dollars were costed at. A delegated
  agent's supplied total can record the model it ran on, `routing.effort` sets the reasoning effort
  builders and reviewers are spawned at, and the report states the effort each unit was
  dispatched at. `sprint.py resume` warns, before a large session is carried into a wave, what
  re-reading its context will cost. Delivered by US0999, US1000, US1143, US1144, US1145,
  US1149, US1150, US1151, US1165 and US1166.
- **Each review seat has a record, an escaped defect is traced to the approval that missed it,
  a seat learns only from a signed run, and a high-risk unit gets a second independent seat.**
  `critic.py brief` names the file the reviewer writes its verdict to, its record command names
  the seat that built the unit, `critic.py record --from-verdict` binds the row to that file's bytes, and a verdict
  written by the context that edited the unit is recorded as a self-review. `retro.py seats`
  scores each seat on its own verdicts and the units it built, and charges each later bug to
  the approval that missed it. A bug filed with `--escaped --shipped-in <release>` records that
  it reached production, `escape.py trace` finds the unit and review that let it through, and
  `escape.py to-class` turns its root cause into a failure class later builds and reviews are
  given. `persona_memory.py` keeps each seat's learnings: a seat writes one from its own record,
  another seat approves it, `sprint close` lists it, and it reaches a brief only once a signed
  close has listed it, unless `sprint.py sign --strike` strikes it. `risk.components` maps paths
  to a risk class, `sprint plan` shows each unit's class, and a high-class unit's brief names
  which of its two independent seats it briefs. Delivered by US1011, US1012, US1013, US1015,
  US1058, US1059, US1061, US1062, US1064, US1065, US1066, US1067, US1068, US1152, US1153,
  US1154, US1157, US1158 and US1159.
- **The front door is written for a head of engineering.** The README is a front door of about
  1,300 words that offers three routes in: evaluate, try and upgrade. Its longer passages moved
  to [why SDLC Studio](why-sdlc-studio.md) and [the install guide](INSTALL.md).
  [The engineering leaders page](engineering-leaders.md) covers change approval, the separation
  of author, reviewer and signer, the signed report and cost in dollars a point, each claim
  linked to what enforces it, and [the support page](../SUPPORT.md) says what support exists and
  where to ask. The product's personas now name a head of engineering in an audited
  organisation as Primary and the chair of the change approval board as Served, and the PRD's
  mission opens "Human in the lead, not just in the loop." Delivered by US1146, US1147, US1148,
  US1162, US1163 and US1164.

## Changed defaults and new refusals

No 6.4 fragment is filed under Breaking, Removed or Security. These are the changes a 6.3 habit
meets as a new refusal or a changed default, each with what to do instead:

- **`critic.py record --from-verdict` refuses a verdict file already recorded.** It exits 2
  and writes nothing for a file whose bytes an earlier row's `Source` already carries, decided
  on the hash, so a copy at a fresh path is refused too, or whose `UNIT` line names another
  unit. The refusal names the earlier row or the mismatched line.
  Instead: record each review from the fresh verdict file its own `critic.py brief` names, and
  brief the seat again for another round.
- **A verdict written by the context that edited the unit is recorded as a self-review.**
  Whatever reviewer name it carries, a verdict from a context that made a Write, Edit or
  NotebookEdit call on one of the unit's Affects files before it first received a verdict path
  briefed for the unit gains `self-review:<path>` in its `Source` cell. The row fails the
  close's review-coverage step and `sprint.py sign`'s review bar; nothing new is refused at
  Done. The check reads the session's Claude Code transcripts, and an edit made through Bash is
  not seen.
  Instead: brief a fresh context that did not edit the unit with `critic.py brief`, and record
  the verdict it writes.
- **The delivery verdict ledger gains a `Source` column.** `sdlc-studio/reviews/critic-verdicts.md`
  gains a ninth column, `Source`, before `Issues`: the hash of the verdict file a brief issued,
  or `-` for a verdict given by `--verdict`, by stdin or from any other file, which `record`
  prints was transcribed. The first verdict recorded after upgrading pads every earlier row
  with `-`, and a 6.3.0 install reads a nine-cell row as malformed and skips it.
  Instead: upgrade every clone that records or reads verdicts together, run the record command
  the brief's footer prints, which reads the verdict file with `--from-verdict`, and commit the
  verdict file with its row.
- **`pricing.copilot_billing` defaults to `tokens`.** A Copilot run's models are priced from
  their AI-credit rates in the Dollar cost row, and its premium requests are counted on their
  own row, unpriced, where 6.3 priced them. Any value other than `tokens` or `requests` is
  refused by name.
  Instead: a plan still billed per premium request, such as a Copilot Pro or Pro+ annual plan,
  sets `pricing.copilot_billing: requests` in `sdlc-studio/.config.yaml`.
- **The report cites the committed run record, not `.local/run-state.json`.** Each figure a
  report reads from the run record cites `sdlc-studio/reports/runs/<RUN-ID>.json`, the record
  the close commits beside it, its not-measured reasons included, where it cited
  `sdlc-studio/.local/run-state.json`, which only the closer's clone holds. A page filed before
  still checks VALID, because `check` compares figures and never their sources.
  Instead: point a reader that follows a figure's source at the run record under
  `sdlc-studio/reports/runs/`.
- **The run record names its plan by digest.** The committed run record carries `plan_digest`,
  `sha256:` and the digest of the plan the run opened from, and its `plan` is now null; a record
  filed before keeps its `plan`.
  Instead: match a saved `sprint-plan.json` to its run by `plan_digest`, not by `plan`.
- **A pytest Verify line that ran only in part fails.** `verify_ac run` no longer stamps
  `Verified: yes` on a pytest criterion whose run passed some tests and skipped others: its FAIL
  line names what was skipped and the reason pytest gave, and each story's line carries
  `partly_skipped=N`. A target that skipped everything keeps its own all-skipped verdict.
  Instead: make the skipped tests run where the criterion is verified, or narrow the Verify
  line to the tests that run there.
- **`transition.py set <story> Ready` refuses a criterion with more than one Verify line.** The
  move to Ready names each stacked criterion and its further Verify lines in `verify_ac lint`'s
  own words, and `--force` does not waive it.
  Instead: split the criterion in two, one Verify line each.
- **`sprint.py resume` warns before a large session is carried into a wave.**
  `sprint.fresh_session` defaults to `warn`: over 80,000 tokens of context, `resume` and
  `sprint.py plan --write` warn on stderr with the context, the cost of re-reading it and the
  remedy. Under `block`, `resume` also exits 2; `plan --write` never refuses.
  Instead: run `sprint.py handoff`, then `sprint.py resume` in a fresh session, or set
  `sprint.fresh_session: off` to read nothing.
- **The sprint report has new rows and envelope keys.** Its Estimates table sets forecast beside
  actual on the cost and span rows, its appendix carries a Prices table, its cost section states
  the effort builders and reviewers were dispatched at, and the JSON page carries the `evidence_schema`, `cost_forecast`
  and `dispatch_effort` marks; a page filed before them re-derives as it was filed.
  Instead: have a parser of the JSON page tolerate keys it does not know, as the evidence
  annex's Versioning section requires.

## Upgrading from 6.3

Reinstall, then carry each project across:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: lists what it would change, writes nothing
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # restamps the project version, and nothing else
```

**Reinstall.** A plain `install.sh` or `install.ps1` fetches the latest published release; pass
`main` as the version for the moving branch.

**`migrate`** is the dry run: it writes nothing. For a 6.3 project it reports one deterministic
upgrade, the version stamp (`sdlc-studio/.version stale (skill 6.3.0 -> 6.4.0)`), beside
anything it leaves to you, such as a seat role with no card.

**`migrate --apply`** writes that stamp to `sdlc-studio/.version` and changes nothing else. It
writes none of the keys below to your `.config.yaml`, so a project reads each at its default
until it sets it.

6.4 adds these configuration keys:

- `risk.components`, default `{}`: path prefixes mapped to `standard`, `elevated` or `high`;
  with no map every story is standard.
- `routing.effort.builder` and `routing.effort.reviewer`, default `inherit`: the reasoning
  effort each unit's builder and reviewer are spawned at; `inherit` is the session's own.
- `routing.effort.reviewer_below_builder`, default `""`: a decision id that lets a reviewer's
  effort sit below its builder's, which `sprint plan` otherwise refuses.
- `pricing.copilot_billing`, default `tokens`: the basis a Copilot plan bills on.
- `personas.memory.validity_days`, default `90`: days from a learning's `Added` to its
  `Review-by`.
- `personas.memory.inject_max`, default `5`: the most live learnings a seat's brief carries.
- `sprint.fresh_session`, default `warn`: what `resume` and `plan --write` do with a large
  session.

## Known issues

Every open finding this release ships is listed by id on [the disclosure page](known-issues.md),
which `tools/known_issues.py write` generates from the bug corpus at the cut, together with the
count below, so the two cannot disagree.

**v6.4.0 discloses 369 open defects: 65 Medium, 304 Low.**

## For contributors to this repository

This repository's own tooling, which does not ship, changed too: the push gate holds a passing
suite to CI's green-run noise budget, so a line a passing test prints refuses the push rather
than turning CI red after it; a test module or class marked as a sweep joins every commit's test
selection; and the lane watchdog's test no longer fails at random on a slow runner. The CHANGELOG
lists each change.

## Sources

Unit ids behind each passage, in this repository.

| Passage | Ids |
| --- | --- |
| Figures | RPT0028, RPT0032 and RPT0033 (`sdlc-studio/reports/`), each report's Estimates table |
| A release carries evidence a change board accepts | US0992, US0993, US0994, US0995, US0996, US0997, US0998, US1155, US1156, US1160, US1161, BG1439 |
| A run's cost is forecast before it starts | US0999, US1000, US1143, US1144, US1145, US1149, US1150, US1151, US1165, US1166 |
| Each review seat has a record | US1011, US1012, US1013, US1014, US1015, US1016, US1058, US1059, US1061, US1062, US1064, US1065, US1066, US1067, US1068, US1152, US1153, US1154, US1157, US1158, US1159 |
| The front door is written for a head of engineering | US1146, US1147, US1148, US1162, US1163, US1164, BG1487 |
| Changed defaults and new refusals | US1013, US1015, US1012, US1011, US1145, US0997, US0998, BG1005, BG1395, BG1343, US1149, US1000, US1151, US1166, US0996 |
| Upgrading from 6.3 | US1152, US1165, US1145, US1058, US1059, US1149, BG1468 |
| For contributors | BG1493, BG1494, US1167 |
