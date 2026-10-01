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
| CR0604 | Complete | D0290: one paragraph in `reference-sprint.md`; no derived domain record, no refusal |
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
| RFC0060 | Accepted when CR0604 completes | WS2 (US0866) Won't Implement under D0290; WS4 shipped as doc |
| RFC0009 | Accepted | the non-vocabulary status "Accepted (partially superseded)" normalised |
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
