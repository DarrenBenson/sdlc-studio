# Discovery backlog sweep, 2026-10-01

Operator instruction: groom the discovery backlog to only actionable epics and stories, closing
anything superseded or that slows the project, with no constraint ratchet (no new gate,
refusal, required flag, ledger, report section or operator question) and efficiency in every
delivered task. Ruling: **D0291** (product seat, subject `backlog:discovery-sweep-2026-10-01`).
Operating domain: **D0290** (operator; supersedes D0239). Plan:
`~/.claude/plans/ultrathink-a-plan-to-squishy-wigderson.md`.

Test applied to every item: keep work a user or the loop measurably benefits from that shrinks
or holds the loop's cost; close what shipped work supersedes (D0264), what adds machinery, and
what costs more than it returns. Every superseding commit below was checked on `main`
(`git merge-base --is-ancestor`); every kept premise is executed at HEAD before grooming.

## Change requests

| ID | Verdict | Superseder / reason |
| --- | --- | --- |
| CR0503 | Superseded | US0923 (`3f18c771`) - brief provenance retired; a verdict records with or without it |
| CR0524 | Superseded | US0918 (`2bc6eb15`) - one verdict ledger decides whether a unit was reviewed |
| CR0596 | Superseded | US0892 (`e21911a2`) - the LC-006 hit it cites is fixed |
| CR0597 | Superseded | BG0760 (`cdd8b105`) - the hand-maintained lane pins are retired |
| CR0598 | Superseded | US0936 (`0e7f580e`) - the caller-less `row_staleness` is deleted |
| CR0563 | Superseded (merge) | CR0559 - same refusal round-trip theme; becomes CR0559's near-miss story |
| CR0581 | Superseded (merge) | CR0590 - only its AC1 survives, as part of the handoff story |
| CR0509 | Rejected | AC1 already holds; AC2 is a new ledger field |
| CR0530 | Rejected | a planner figure for a parallel flag the loop no longer ships |
| CR0546 | Rejected | a new close-report row; `close_owed detect` already sees out-of-batch work |
| CR0551 | Rejected | idle-time classification is new measurement machinery for a breaker that rarely trips |
| CR0588 | Rejected | a strict run-state reader API for a one-off, with no recurrence |
| CR0600 | Rejected | its hits are a stale test comment and a commit credit; nothing worth fixing |
| CR0602 | Rejected | the minutes forecast already ships (RPT0013); the transcript-path half is open BG0835 |
| CR0604 | Rejected | D0290: the rule ships as one paragraph in `reference-sprint.md`; no stop-detection machinery, derived domain record or refusal is built |
| CR0534 | Decomposed | US0759 reshaped: `config show --sources` (2 pts) |
| CR0552 | Decomposed | US0784 reshaped: retire the advisory revert-check lane (2 pts, a deletion) |
| CR0559 | Decomposed | US0804 `--unit` (1), US0805 flag-spelled `--fields-file` keys (2), near-miss hint (1) |
| CR0590 | Decomposed | the report replaces the handoff page (5 pts, a deletion) |
| CR0592 | Decomposed | themed stories; bullet verdicts below |
| CR0601 | Superseded (merge) | folded into CR0592's "a v5 upgrade reads clean" story |
| CR0603 | Decomposed | #4 quick start installs a verified release (2 pts); #1-#3 rejected |

## RFCs and epics

| ID | Verdict | Reason |
| --- | --- | --- |
| RFC0058 | Accepted | D3, D5 and D6 declined or closed (no consult gate or artefact); US0838 Won't Implement |
| RFC0060 | Accepted | WS2 (US0866) Won't Implement and WS4 (CR0604) documented under D0290; WS1 superseded, WS3 shipped as `decisions.py rule` |
| RFC0009 | unchanged | its `Accepted (partially superseded)` status is deliberate and pinned by tools/tests/test_supersession_records.py; the tooling already reads it as Accepted. Normalising it was reverted |
| RFC0030 | unchanged | already Accepted, terminal (D0027 "build on demand") |
| EP0258 | Superseded | all six stories were Superseded; it read Done |
| US0707, US0722, US0730, US0732, US0745, US0777, US0783 | Won't Implement | children of the requests closed above |
| US0750, US0774 | Won't Implement | orphans: parents CR0531 Rejected and CR0545 Superseded |
| US0838 | Won't Implement | RFC0058's consult gate (AC1/AC3 were exit-2 refusals) |
| US0866 | Won't Implement | D0290: no derived domain record or plan refusal |
| EP0222, 0225, 0227, 0230, 0231, 0236, 0237, 0238, 0256, 0259 | Superseded | settled by `reconcile settle`: every child terminal |

## Config and lessons

- `triage.low_consolidation: false` - the consumer default; the bucket had grown to a 72-item sweep.
- Lesson classes whose graduation CR closed: LC-002, LC-003, LC-006, LC-008 to `graduated`;
  LC-004 to `retired` (CR0600 rejected, nothing to fix). The lesson-graduation generator stays
  (D0252); a groomed story makes the class finish its own lifecycle.

## CR0592 and CR0603 bullets

CR0592's 72 bullets, numbered in file order, each executed at `5ec11117`; no script changed
between that ref and `85042135`. The bucket is now empty.

| Verdict | Bullets | Reason |
| --- | --- | --- |
| FIXED | #3, 4, 5, 7, 8, 10, 11, 12, 13, 29, 59 | shipped |
| DUPLICATE | #39 | of #70 |
| REJECT | #1, 2, 9, 14, 15, 16, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 36, 38, 40, 43, 45, 49, 50, 51, 52, 53, 55, 56, 57, 67, 68, 71, 72 | below cost, mutant or pin residue, or the fix would add a gate |
| SEPARATE | #63 | BG0866 |
| KEEP | #17, 20, 33, 44 | US0969, a CLI never reports success it did not get |
| KEEP | #32, 46, 58 (objects half) | US0970, the finding writers keep what they were given |
| KEEP | #58 (`type` key half) | US0805 |
| KEEP | #47, 48, 61, 69 | US0971, a fresh project's first plan is quiet and correct |
| KEEP | #30, 35, 41 | US0972, derived figures read honestly |
| KEEP | #34, 37, 54, 62, 70 | US0973, docs and comments tell the truth |
| KEEP | #31, 60, 64 | US0974, a v5 upgrade reads clean |
| KEEP | CR0601 (merged) | US0975, migrate reports retired v5 surface in a project's own docs |
| KEEP | #42, 65 (parts 1-2), 66 | US0976, install and upgrade never damage a consumer's files |
| KEEP | #6 + graduation by close_pass | US0977, a lesson class finishes its lifecycle |

CR0603: #4 is US0968; #1 (marker machinery), #2 (decision-log machinery) and #3 (a new flag)
are rejected. The bucket is now empty.

## Delivery bugs

| ID | Verdict | Reason |
| --- | --- | --- |
| BG0691, BG0696, BG0706, BG0739, BG0840 | Won't Fix | below cost, or already fixed |
| BG0740 | Superseded | by US0926 |
| BG0737 | Groomed | 1 point; criteria executed by the sweep's evidence agent |

## Surviving work

Every unit below carries authored criteria with a Verify selector, Points, Affects and one
premise executed at HEAD.

| ID | Title | Points | Parent |
| --- | --- | --- | --- |
| US0759 | `config.py show --sources` marks each key in force as a skill default or project-set | 2 | EP0233 / CR0534 |
| US0784 | The advisory `revert-check` gate lane is retired; the per-unit CLI stays | 2 | EP0239 / CR0552 |
| US0804 | `verify_ac.py run --unit <id>` is accepted as an alias for `--id` | 1 | EP0244 / CR0559 |
| US0805 | A `--fields-file` key spelled as the verb's own flag is accepted | 2 | EP0244 / CR0559 |
| US0966 | `verify_ac.py run` names the near-miss node | 1 | EP0244 / CR0559 |
| US0967 | The close writes no handoff; the next plan reads the signed report | 5 | EP0268 / CR0590 |
| US0968 | With no `--version`, install.sh installs the latest verified release | 2 | EP0269 / CR0603 |
| US0969 | A CLI never reports success it did not get | 3 | EP0270 / CR0592 |
| US0970 | The finding writers keep every criterion and verifier they were given | 3 | EP0270 / CR0592 |
| US0971 | A fresh project's first plan is quiet and correct | 3 | EP0270 / CR0592 |
| US0972 | Derived figures read honestly | 3 | EP0270 / CR0592 |
| US0973 | Docs and comments tell the truth | 2 | EP0270 / CR0592 |
| US0974 | A v5 upgrade reads clean | 3 | EP0270 / CR0592 |
| US0975 | migrate reports where a project's own docs name retired v5 surface | 3 | EP0270 / CR0592 |
| US0976 | Install and upgrade never damage a consumer's files | 3 | EP0270 / CR0592 |
| US0977 | A lesson class finishes its lifecycle | 2 | EP0270 / CR0592 |
| BG0866 | js-yaml 5.2.2 sits inside Dependabot alert 19's range | 1 | - |
| BG0737 | the stale downgrade destroys an author's reason | 1 | - |

Total: 42 points.

## Delivery bugs, value pass (every open bug re-executed at HEAD `de4470fa`)

Kept, groomed with runnable criteria and a `Groomed:` evidence line (29 pts): BG0726 (1),
BG0817 (1), BG0825 (3), BG0827 (1), BG0833 (1), BG0860 (2), BG0861 (3, as the retirement of
the dead batch-span code), BG0824 (2), BG0831 (3), BG0832 (1), BG0834 (1), BG0835 (1, takes
CR0602's transcript half), BG0837 (3), BG0839 (2), BG0855 (2), BG0858 (2, depends on US0974),
plus BG0737 (1) and BG0866 (1) groomed earlier today.

| Closed | Status | Reason |
| --- | --- | --- |
| BG0701 | Won't Fix | the cause half fixed by US0876 (`5dfee925`); the handoff half goes with US0967; the rest is rolling-run edge consistency, below cost under D0290 |
| BG0828 | Won't Fix | the fix adds warnings and fingerprint validation; US0923 made a verdict record with or without a brief |
| BG0830 | Won't Fix | the fix is a new refusal guard on a sealed run |
| BG0863 | Won't Fix | only a corrupted ledger reaches it; the dry run already reports the gap and the real close raises |
| BG0864 | Won't Fix | the fix adds a refusal; accepting a missing run is the documented contract (help/bug.md) |
| BG0712 | Won't Fix | the fix makes the budget guard refuse five files today; 110 lines of headroom remain |
| BG0734 | Won't Fix | a harmless two-line dead branch; delete it the next time the file is edited |
| BG0752 | Won't Fix | widening per-commit selection slows every commit; the push runs the full suite |
| BG0754 | Won't Fix | all six of its own fixes shipped; the residue is the hub selection's size, unmeasurable as a test |
| BG0838 | Won't Fix | tightens a doc-scanning guard (new refusals); its installed-copy half is US0975 |
| BG0857 | Won't Fix | a chmod-000 workspace directory is contrived; the fix adds a new failure |
| BG0836 | Won't Fix | duplicate of US0977 |
| BG0841 | Superseded | BG0850 (`bb098240`) discharges carried units; raising `max_rounds` under a recorded decision stays the way through |

Also closed: SC0001 (charter) Withdrawn - its scope (CR0507 Superseded, CR0510 Complete) is
finished; TS0001 and TS0002 Complete - their epics EP0010 and EP0011 are Done. US0759 and
US0969 now use `review.max_rounds` as their example key, since BG0831 retires `review.policy`.
