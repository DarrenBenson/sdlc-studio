# Evidence from the runs

Every sprint run of SDLC Studio that its operator signed, one row per run, read from the run's
latest signed report of record in `sdlc-studio/reports/`. Nothing in the table is typed by hand:
the table is written by the command under [Regenerating this page](#regenerating-this-page), and
the same command checks that it still matches the reports. A report nobody signed is left out.
Dollars per point reads not recorded for a run whose report predates that figure, and NOT
MEASURED where the report itself recorded that the cost could not be priced. Model names each
`price_model` the report priced or, where it priced none, each `model_name` its tokens-by-model
rows give, or, where it has neither, the `model` figure of its cost section, and reads not
recorded where none of these names a model. The reports do not yet record the harness each run
ran in, so the table cannot show it; CR0743 adds that record.

## The runs

<!-- BEGIN GENERATED -->
The newest report this page covers is RPT0045, signed at 2026-11-25T13:43:47Z.

Each column reads one field of the report its row names:

- Run: `run_id`.
- Report: `report_id`.
- Goal verdict: `goal_verdict` in the `goal` section.
- Verdict note: `goal_verdict_note` in the `goal` section, shown when the verdict is not Judged achieved and `-` when it is, or not recorded where the report holds no note.
- Dollars per point: `est_actual` of the `estimates` row whose `est_measure` is Dollars per point, or not recorded where the report holds no such row.
- Model: `price_model` of each `cost_prices` row, or, where the report priced no model, `model_name` of each `cost` row that names one rather than mixed or unrecorded, or, where it has neither, the `model` figure of the `cost` section when that names one, or not recorded where none of these names a model.
- Hours to signature: the hours from `generated_at` to `signature.signed_at`.

| Run | Report | Goal verdict | Verdict note | Dollars per point | Model | Hours to signature |
| --- | --- | --- | --- | --- | --- | --- |
| RUN-01M87B5M | RPT0045 | Judged achieved | - | $4.70 | claude-opus-5-5, claude-sonnet-5-5 | 0.2 |
| RUN-01M866KQ | RPT0044 | Judged achieved | - | $2.94 | claude-opus-5-5, claude-sonnet-5-5 | 0.1 |
| RUN-01M84Z8Z | RPT0043 | Judged achieved | - | $2.94 | claude-opus-5-5, claude-sonnet-5-5 | 0.1 |
| RUN-01M836YT | RPT0042 | Judged partial | 24 of the 25 planned Medium bugs fixed, each on an independent APPROVE with a test that fails without the fix; BG0967 (Medium) did not converge in three rounds and is carried under BG1723 for a rule-based redesign in run twenty-four | $4.17 | claude-opus-5-5, claude-sonnet-5-5 | 0.1 |
| RUN-01M80RTZ | RPT0041 | Judged partial | 25 of the 28 planned Medium bugs are Fixed, each with a test that fails without its fix (every unit approved by an independent qa review, 13 of them in a ruled third round); BG1475, BG1532 and BG1625 were rejected in their ruled third rounds and carry to the next run under BG1707, BG1714 and BG1717. Three Lows filed this run (BG1700 to BG1702) were added and Fixed. | $4.79 | claude-opus-5-5 | 0.1 |
| RUN-01M7YPFD | RPT0040 | Judged partial | 31 of the 32 Medium bugs in the sprint, lane, transition and verify scripts are Fixed, each with a test its mutation pass shows fails without the fix; BG1534 is carried open after its ruled third round rejected | $3.65 | claude-opus-5-5 | 0.1 |
| RUN-01M7VNR0 | RPT0039 | Judged partial | Partial. Clause two (each seat's goal brief uses its own card) is achieved by all three close-time seats; clause three (persona docs match the code) by two of three, product reading partial over BG1669's missing persona_review.py owed entry. Clause one is partial by all three: the enforced standard holds (persona_review.py check blocks=0, and every entry point that frames from a card refuses a held one), but this repository's own seven cards carry no Evidence section and are owed a review (BG1666), so the cards meet the blocking rules only. The close panel reads the partial answers as unanswered (BG1673). | $2.88 | claude-opus-5-5, claude-sonnet-5-5 | 13.2 |
| RUN-01M7TTK3 | RPT0038 | Judged achieved | - | $2.05 | claude-opus-5-5, claude-sonnet-5-5 | 0.2 |
| RUN-01M7SS62 | RPT0037 | Judged achieved | - | $2.64 | claude-opus-5-5 | 0.1 |
| RUN-01M7QMZ0 | RPT0036 | Judged partial | The repository's front door is done: the GitHub About box, the README first screen, docs/harnesses.md, docs/enterprise.md, the skill metadata and llms.txt present SDLC Studio as harness-agnostic with people in the lead, every claim checked against the tree. CR0742 names the website home page as the third front-door surface; it lives in the website's own repository and is delivered by a change request run there next, so a reviewer who lands on the site still reads the old positioning. | $2.18 | claude-opus-5-5 | 0.2 |
| RUN-01M7NTY5 | RPT0035 | Judged partial | Every gate the audit named now refuses work it never judged, and a run closed in the operator's absence awaits a signature that must name its authority; BG1582 leaves one sign path (HEAD past the close commit, no later run open) that skips the whole-tree check, deferred to the operator | $2.00 | claude-opus-5-5 | 4.9 |
| RUN-01M7HA6R | RPT0034 | Judged achieved | - | $2.08 | claude-opus-5-5 | 0.1 |
| RUN-01M7GEHM | RPT0033 | Judged achieved | - | $2.18 | claude-opus-5-5 | 0.1 |
| RUN-01M7EYR3 | RPT0032 | Judged achieved | - | $2.35 | claude-opus-5-5 | 0.1 |
| RUN-01M7E52T | RPT0031 | Judged achieved | - | $2.27 | claude-opus-5-5, claude-sonnet-5-5 | 0.1 |
| RUN-01M78TKD | RPT0030 | Judged partial | All 24 planned units, 49 points, delivered on independent APPROVEs (four after one repair round each). Lanes land and die cleanly (BG1336, BG1337, BG1339, BG1344, BG1261, BG1262) and verifiers no longer read green wrongly or leak (BG1005, BG1009, BG0991, BG1112, BG1190, BG1228). Cost is priced over the whole window and for long Grok prompts (BG1279, BG1305, BG1330, BG1331), but every lane this run was multi-unit and lane return cannot split one builder's total, so per-unit cost stays unpriced (BG1397). BG1420, added when the push gate found five red tests, fixed them but was carried as BG1425 after its repair's round-2 review. | $2.28 | claude-opus-5-5, claude-sonnet-5-5 | 35.3 |
| RUN-01M77177 | RPT0029 | Judged achieved | - | $2.22 | claude-haiku-5-5, claude-opus-5-5 | 0.1 |
| RUN-01M7061X | RPT0028 | Judged achieved | - | $2.48 | not recorded | 15.7 |
| RUN-01M6RZQZ | RPT0027 | Judged partial | Run seven's cost features now hold: all seven hardening bugs are Fixed and the non-Claude models are priced (US1135), and every agent starts leaner (AGENTS.md at 6,580 chars, the lean builder and reviewer definitions at about 16k start context against 34k). Commits got only partly leaner: the self-written trailers landed after a carry (US1133, fixed in-run as BG1274), the quiet commit path (US1134) went to 6.4 under D0419, and Copilot's token billing (CR0685) and the pricing gaps (BG1266) are carried. | $2.89 | not recorded | 0.7 |
| RUN-01M6RAP7 | RPT0026 | Judged partial | Every supported CLI harness is now metered on one normalised basis, per lane through lane run and per session through the Copilot, OpenCode and Codex readers, with dollars per model and a per-role table; partial because the role table reads the whole session rather than the run (BG1254), only Claude models are priced so far, a two-model lane session prices at one model (BG1252), and the benchmark cannot yet run a real session (BG1248) | NOT MEASURED | not recorded | 0.4 |
| RUN-01M6NH7W | RPT0025 | Judged achieved | - | not recorded | not recorded | 13.8 |
| RUN-01M6F74P | RPT0024 | Judged partial | The release verify lane ran at default ceilings in 1,272 s on the gate host (6.2.0's took 4,447 to 6,582 s) and band drift and the commit frictions are fixed, but the one release gate on the closing commit did not pass first time: three criteria need Python 3.10 and pdftotext, which the gate host lacks (BG1220), one red came from a filed bug's own text, and the fragments lane refuses any commit before a cut. | not recorded | not recorded | 9.4 |
| RUN-01M6A3K2 | RPT0023 | Judged partial | Every lesson is judged and the commit gate fell from 38.6s to 14.6s, but the push gate stayed at about 610s and filed false sentences remain in the TRD, TSD and a persona card (D0394) | not recorded | not recorded | 0.0 |
| RUN-01M5EM9N | RPT0022 | Judged partial | The self-check gate, the priced cost meter and the regression flag shipped and hold on main; 6.2's blockers (BG0963 and the rest) moved to run four, and the run's own cost per point did not improve. | not recorded | not recorded | 91.5 |
| RUN-01M59TRM | RPT0021 | Judged partial | Every clause of the goal holds on main, but two of the eleven units are carried, so the definition of done recorded at goal review (all eleven terminal, plus a live proof) is not met. Pushes are judged on devserver1 against exactly the commit pushed, proven live (US1075, US1077, US1078). The TRD and TSD were judged accurate (US1084, US1085, and US1086's documents). The weekly run reads true: dispatched run 39389634097 has corpus-verify at red-criteria 0, baseline 0 (BG1054, BG1099). US1076 (BG1078) and US1086 (BG1095) hit the review cap on test repairs that did not converge; their behaviour and documents are on main. | not recorded | claude-opus-5-5 | 5.9 |
| RUN-01M4R168 | RPT0020 | Judged achieved | - | not recorded | claude-opus-5-5 | 1.5 |
| RUN-01M45FV6 | RPT0019 | Judged achieved | - | not recorded | claude-opus-5-5 | 0.2 |
| RUN-01M40TSJ | RPT0018 | Judged achieved | - | not recorded | claude-opus-5-5 | 0.0 |
| RUN-01M3ZAGE | RPT0016 | Judged achieved | - | not recorded | claude-opus-5-5 | 7.0 |
| RUN-01M3Y7DP | RPT0015 | Judged achieved | - | not recorded | claude-opus-5-5 | 4.5 |
| RUN-01M3VF2J | RPT0014 | Judged achieved | - | not recorded | claude-opus-5-5 | 11.5 |
| RUN-01M3T8N1 | RPT0013 | Judged achieved | - | not recorded | claude-opus-5-5 | 0.1 |
| RUN-01M3RPSK | RPT0012 | Judged achieved | - | not recorded | claude-opus-5-5 | 0.8 |
| RUN-01M3HR74 | RPT0011 | Judged achieved | - | not recorded | not recorded | 2.9 |
| RUN-01M3CK1K | RPT0010 | Judged achieved | - | not recorded | not recorded | 1.9 |
| RUN-01M3BK9Y | RPT0009 | Judged partial | History-aware review landed in full: every lane brief carries its files' history and prior art, and goals trace to PRD outcomes (CR0594, EP0264). Eleven of twelve review-paperwork deletions landed; the repair ledger (US0914) is still read, cut under D0269 because deleting it strips critiqued from 35 historical units. 35 of 36 batch units, 111 points. | not recorded | not recorded | 0.2 |
| RUN-01M39MC0 | RPT0008 | Judged partial | Half one missed by 3s: a one-line gate.py commit measured 93s end to end against 90 (229s at the start), with its suites down to 43s; code commits this run cleared in 60-75s. The rest is the sequential pre-commit, as US0891 was carried (BG0759). Half two not delivered: US0904's lane-yield log was carried at the review cap on a one-character defect (BG0761). Deleted: the warning ratchet, verify ratchet, boundary roster and release-notes count pin, plus eight advisory lanes off the commit. | not recorded | not recorded | 1.7 |
| RUN-01M3891F | RPT0007 | Judged partial | The sprint learns from repeated mistakes without being told: lessons are failure classes that count repeats from retros and cited REJECTs, reach the plan, build and review briefs, graduate to a CR on a second repeat and retire when quiet, with a bundled seed for new projects (US0887, US0888). Commits do not yet clear in about a minute: a paperwork commit clears in seconds and a push fell from about 750s to 284s, but a code commit that reaches a widely imported script still took 165-258s under this machine's load against the 90s budget (BG0754). | not recorded | not recorded | 1.5 |
| RUN-01M36R3D | RPT0006 | Judged achieved | - | not recorded | not recorded | 5.2 |
| RUN-01M33WJ3 | RPT0005 | Judged partial | Clauses 1-3 delivered in full; Clause 4 - a goal authored as checked clauses with a derived verdict - NOT attempted, dropped to the next run with EP0258 intact under D0250. This verdict is ASSERTED by its author because nothing yet derives it, which is exactly what Clause 4 exists to end. | not recorded | claude-opus-5 | 7.6 |
| RUN-01M306PY | RPT0003 | Judged achieved | - | not recorded | claude-opus-5 | 1.3 |
| RUN-01M2SPNS | RPT0002 | Judged achieved | - | not recorded | claude-opus-5 | 21.1 |
<!-- END GENERATED -->

## What Judged partial means

The closing review judges each run against its Sprint Goal, and the close records that judgement
as achieved, partial or missed, with a note giving the reason
([the loop](../.claude/skills/sdlc-studio/reference-sprint.md#the-loop)). Judged partial means the
run delivered work but did not reach its goal as worded. The goal cannot be reworded once the
verdict is recorded, so a partial verdict stands as the reading of a run that fell short.

The reason shown beside a partial verdict is that note, printed as the report holds it: the
`goal_verdict_note` figure of the report's `goal` section
([report figure keys](../.claude/skills/sdlc-studio/reference-evidence-schema.md#report-figure-keys)).
A run judged achieved carries a note too; the table shows `-` for it, and the note is in that
run's report. A note reading not recorded is one the report never held.

## How the wait for a signature is measured

Hours to signature runs from the moment the report of record was built, at the run's close, to
the moment the operator signed it. The first is the report's `generated_at`; the second is
`signature.signed_at`, written when the operator signs
([report envelope keys](../.claude/skills/sdlc-studio/reference-evidence-schema.md#report-envelope-keys)).
It is the time a finished run waited for its accountable person to read and sign the evidence,
not the time the run took. A long wait is a run signed after a night, a weekend or a review of
its own; the report's figures do not change while it waits, because signing seals the report
that was built.

## Regenerating this page

Run this from the repository root after a run is signed:

```bash
python3 .claude/skills/sdlc-studio/scripts/sprint_report.py evidence --out docs/evidence.md
```

It rewrites the table between the generation markers and leaves every other line of this page
as it is. Add `--check` to write nothing: it exits 1 naming each run whose row differs from the
reports the page names, so a hand-edited cell is caught. A report signed after the newest one the
page names is reported as not yet on the page and does not fail the check, so closing a run never
turns it red; the page catches up when it is regenerated. The command is described with the rest
of [`sprint_report.py`](../.claude/skills/sdlc-studio/reference-scripts-domain.md#sprint_reportpy).
