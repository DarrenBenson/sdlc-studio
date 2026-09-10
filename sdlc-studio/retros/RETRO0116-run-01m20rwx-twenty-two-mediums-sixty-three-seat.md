# RETRO-0116: RUN-01M20RWX: twenty-two Mediums, sixty-three seat verdicts, and the gate that caught its own repair

> **Date:** 2026-09-10
> **Batch:** BG0490, BG0493, BG0567, BG0578, BG0591, BG0601, BG0608, BG0612, BG0627, BG0630, BG0633, BG0637, BG0654, BG0655, BG0656, BG0657, BG0658, BG0660, US0819, US0820, US0821, US0822
> **Goal:** every Medium open at this run's base ref is disposed of - terminal with its own verifiers passing, or ruled open with a date and a reason - and so is any this run itself files
> **Delivered:** 22 / 22   **Blocked:** 0

## Delivered

- BG0490 - `check_versions` extracts a version by structure only; both prose fallbacks are gone
- BG0493 - the practice-rules lane is EXECUTED against two trees the checker judges differently, and the hook's own `run` helper is exercised rather than described
- BG0567 - the upgrade baseline is captured from a pinned commit with `git archive`, and the ARGUMENTS both sides run are asserted, not only the outputs
- BG0578 - a test file's subject is declared rather than counted, read from the head of the file only
- BG0591 - `status` and `close_owed detect` name the same blocking SET, not just the same verdict
- BG0601 - the dry-run parity sweep compares a resolver's whole answer, through the one helper its own criteria drive
- BG0608 - the budget line leads with the verdict it judges on and stops stating a drift percentage across selection widths
- BG0612 - the checklist roster is named rather than counted, and its resolver check runs at import
- BG0627 - `prose_value` replaces the `or ""` guard at ten call sites, and a non-string prose field is refused by name at the two entry points that mint prose
- BG0630 - the test-plan gate fires at the TERMINAL transition by whatever route reached it, and states one absence once
- BG0633 - `annotate` checks the vocabulary it writes
- BG0637 - the review ledgers escape for the context and refuse a value they cannot write
- BG0654 - `enable-hooks.sh` sets a keepalive on the clone's ssh and leaves one you set alone, naming the scope it found it in
- BG0655 - a retracted mutation row stops being read as a survivor
- BG0656 - the disclosure guard reads the notes of the release being cut, by the rule and not by today's literal
- BG0657 - the corpus lane reports what rose, what went green and what VANISHED, by id
- BG0658 - a Test Plan mutant naming a piped command is no longer truncated at the pipe
- BG0660 - the rehearsal-lane test pays for one lane instead of the whole boundary, and a scan forbids the class
- US0819 - `testplan probe` asks whether a criterion CAN FAIL and reports a PASS as the finding
- US0820 - `sprint plan` refuses a batch carrying an unruled one, three modes, default `report`
- US0821 - a plan ruling is recorded, hashed against the criterion's title AND selector, and withdrawable in place
- US0822 - a ledger row is judged by the site its mutant was applied to, not by a hash of the whole file

## Blocked / deferred

- none. Every unit in the batch reached its terminal status.

## What went well

- **The seats found what the author could not.** 63 verdicts across plan and delivery, 44 of them REJECT, and the strongest findings were all of one shape: a criterion whose words go further than its fixture. The product seat's repo-wide census of US0819's probe - every one of its 25 findings was a unit the same commit had delivered - is the single best measurement any review has produced here.
- **US0822's benefit was found to be unreachable, by a reviewer, before it shipped.** The anchors reached the commit lane and stopped: `plan_execution`, the join the terminal gate reads, still keyed on the whole file's hash. 26 rows across three units went from `not-run` to counted the moment that was fixed.
- **Two seats' blocking findings were REFUTED by execution** rather than accepted - BG0657's dead-stamps count and BG0630's `--force` regression - and recorded as OVER-CLAIMED with the commands that refute them. A review is evidence, not an instruction.
- **Parallel worktrees worked.** Two clusters delivered eight units between them with no lost work, and the only cost was ledger drift, which the anchors this run shipped are what fix.

## What was hard / what stalled

- **The mutation ledger cost more than the code.** 174 rows had to be re-measured because every edit to a shared file staled every unit's evidence in it. US0822 fixes the rule; it does not refund this run.
- **Coverage rulings are hashed the same way**, so the first pass of 471 rulings was spent by the next edit and the whole set had to be re-measured after the last one. Rule after the LAST edit is now true of two ledgers, not one.
- **Three of my own mutants were aimed at the wrong site** and had to be retracted: one applied to a spy test instead of the sweep, one to a fixture whose route could not reach the branch, one that killed on a TypeError rather than on its criterion. Each read as a verdict and was a measurement of nothing.
- **A repair introduced a defect the tool caught**: deduplicating the terminal test-plan gate on the absent-plan fact let its OTHER message land twice, measured on US0822 at its own transition.

## Lessons

- **A criterion's words are law and its fixture is the measurement; when they differ, the fixture wins silently.** Nine of this run's blocking findings were that shape - AC5 naming three grep cases and testing none of them, AC8 saying "judged by RUNNING" while reading source, AC7 requiring a round trip and asserting a substring, AC4's control built on a class the code never emits. The check is cheap: read the criterion, then ask what the test would still pass with removed.
- **A mutant aimed at the wrong site is not weak evidence, it is none.** Three retractions this run. Before recording a verdict, confirm the edit is the one the criterion is about and that the node dies on the criterion's own assertion rather than on an import error, a TypeError or a sibling's clause.
- **A guard's reach is the spelling its fixture used.** BG0660's scan could not see this repository's own `subprocess.run([sys.executable, str(scripts / "gate.py"), ...])`; widening it to read joined strings for every callee then produced four false positives from fixture text. Probe a new detector against every shape the corpus actually contains, in both directions, before believing it.
- **Two readers of one rule will disagree, and the one that blocks is the one nobody tested.** `row_staleness` shipped with no production caller while the lane re-implemented it inline and the terminal gate used the old rule. Wire the new rule into the reader that refuses, or the cost you removed is still being paid.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A criterion's words are law and its fixture is the measurement; when they differ the fixture wins silently, and the criterion reads as met.
- A mutant aimed at the wrong site is not weak evidence, it is none - confirm the node dies on the criterion's own assertion.
- A guard's reach is the spelling its fixture used; probe a new detector against every shape the corpus holds, in both directions.
- Two readers of one rule will disagree, and the one that blocks is the one nobody tested.
- Both evidence ledgers are hashed against file bytes: register and rule after the LAST edit, then re-run every unit's dry-run.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0659 | not-stop-ship | Claude Opus 5 (ruled 2026-09-10, D0186 disclosure half) | 2026-09-10 |
| BG0661 | not-stop-ship | Claude Opus 5 (ruled 2026-09-10, D0186 disclosure half) | 2026-09-10 |
| BG0662 | not-stop-ship | Claude Opus 5 (ruled 2026-09-10, D0186 disclosure half) | 2026-09-10 |
| CR0509 | deferred | Claude Opus 5 (a review worktree's stale base; every reviewer this run worked in /tmp copies taken at HEAD, so the cost did not land) | 2026-09-10 |
| CR0528 | not-stop-ship | Claude Opus 5 (the installed copy is reconciled at the close; this close ran `forward-port.sh --yes` and 25 files were mirrored) | 2026-09-10 |
| CR0529 | deferred | Claude Opus 5 (prior-art scoped to the reviewer; no unit this run was rejected for rediscovering one) | 2026-09-10 |
| CR0530 | deferred | Claude Opus 5 (the planner reports clusters not the parallelisable fraction; two worktrees were split by hand this run and the split held) | 2026-09-10 |
| CR0531 | deferred | Claude Opus 5 (a charter's scope query cannot express a decomposition; no charter was queued this run) | 2026-09-10 |
| CR0533 | not-stop-ship | Claude Opus 5 (revert-check ships advisory and its blind spot is filed as BG0661, ruled open) | 2026-09-10 |
| CR0534 | deferred | Claude Opus 5 (configuration as an introduced surface; this run added `review.plan_falsifiability` to the shipped defaults and the reference, which is the narrow half) | 2026-09-10 |
| CR0535 | deferred | Claude Opus 5 (a refusing verb stating its contract before you trip it; 39 verbs, none of them on this batch's path) | 2026-09-10 |
| CR0536 | deferred | Claude Opus 5 (spec documents not learning about a shipped tool; the three new verbs this run added were documented by hand at the delivery review's insistence) | 2026-09-10 |
| CR0539 | not-stop-ship | Claude Opus 5 (lane-check's 181 units; it reports and blocks nothing, and this run measured one of its readings to be a false positive on `import subprocess as _sp`) | 2026-09-10 |
| CR0546 | deferred | Claude Opus 5 (a run noticing work its batch never named; this batch named all 22 and delivered all 22) | 2026-09-10 |
| CR0547 | not-stop-ship | Claude Opus 5 (revert-check as a blocking requirement; it ships advisory while its yield is measured, which is the recorded decision) | 2026-09-10 |
| CR0569 | not-stop-ship | Claude Opus 5 (DISCHARGED by this run - US0819, US0820 and US0821 are its three units, all delivered and terminal. The request stays open only until it is closed against them) | 2026-09-10 |
| CR0570 | not-stop-ship | Claude Opus 5 (DISCHARGED by this run - US0822 is its unit, delivered and terminal, and the join the terminal gate reads was repaired at the delivery review) | 2026-09-10 |
| CR0424 | deferred | Claude Opus 5 (an RV artefact demanded beside a critic sign-off; this close ran the critic chain and the RV requirement did not fire) | 2026-09-10 |
| CR0441 | deferred | Claude Opus 5 (in-flight sprint controls; this run changed its batch once, by hand, and the cost did not justify the tooling) | 2026-09-10 |
| CR0496 | deferred | Claude Opus 5 (a project-config decision invisible to the forward-port check; the check ran clean here and 25 files were mirrored) | 2026-09-10 |
| CR0497 | deferred | Claude Opus 5 (silent grandfathering at the v5 upgrade; no upgrade was performed this run) | 2026-09-10 |
| CR0499 | deferred | Claude Opus 5 (asking whether a sprint produced a shippable increment; the v5.1 cut this run leads into asks it directly instead) | 2026-09-10 |
| CR0503 | not-stop-ship | Claude Opus 5 (an adversarial review run outside the seat ceremony; every one of this run's 66 verdicts went through `critic.py brief`, and `critic record` refuses a verdict with no brief provenance) | 2026-09-10 |
| CR0504 | deferred | Claude Opus 5 (closing review doing development's work; this run's closing findings were 49 raised outside a batch boundary, which is the number the close reports and the next run drives down) | 2026-09-10 |
| CR0507 | deferred | Claude Opus 5 (the close asking twenty questions; it asked ten stages and two checklist items this time, and both items were real gaps) | 2026-09-10 |
| CR0512 | not-stop-ship | Claude Opus 5 (unit review scope; the rule held all run - two seat findings were recorded OVER-CLAIMED on exactly this ground rather than repaired) | 2026-09-10 |
| CR0515 | deferred | Claude Opus 5 (detecting hand-rolled work from the transcript; not on this batch's path) | 2026-09-10 |
| CR0526 | deferred | Claude Opus 5 (a sprint ending with nothing open; D0186 replaces that bar with a dated ruling per id, which this retro carries) | 2026-09-10 |
| CR0548 | deferred | Claude Opus 5 (deriving `Verification depth` from the ledger; the field was authored by hand this run and no unit was refused for it) | 2026-09-10 |
| CR0550 | not-stop-ship | Claude Opus 5 (the test-plan gate scoped by date alone; it refused three units this run and each refusal was a real gap, so the scope is doing work) | 2026-09-10 |
| CR0551 | deferred | Claude Opus 5 (the appetite ceiling measuring wall-clock; this run stayed inside its 64-unit, 5760-minute appetite) | 2026-09-10 |
| CR0552 | not-stop-ship | Claude Opus 5 (revert-check mutating the live tree; it is advisory and its blind spot is filed as BG0661, ruled open) | 2026-09-10 |
| CR0553 | deferred | Claude Opus 5 (the exemption reason floor counting characters; every ruling this run carries a reason a reviewer can read, and 471 of them were written to one of nine stated reasons) | 2026-09-10 |
| CR0554 | not-stop-ship | Claude Opus 5 (a plan row whose kill node is not the criterion's own verifier; three such rows were caught by hand this run and retracted, which is the cost the request names) | 2026-09-10 |
| CR0555 | deferred | Claude Opus 5 (moving the expensive half of the test-plan gate behind a diff; the gate cost seconds at every transition this run) | 2026-09-10 |
| CR0556 | not-stop-ship | Claude Opus 5 (a bug reaching terminal with no independent judgement of its plan; the gate fired on three units here and each was reviewed rather than waived) | 2026-09-10 |
| CR0558 | deferred | Claude Opus 5 (the derived-depth lane checking a seal rather than re-deriving; no depth field was contested this run) | 2026-09-10 |
| CR0559 | deferred | Claude Opus 5 (one concept named three ways; a vocabulary change across the toolchain is its own unit, not a close item) | 2026-09-10 |
| CR0560 | not-stop-ship | Claude Opus 5 (filing a finding leaving the disclosure page stale; it happened twice this run, both times caught by the suite within one commit, and it is the same class as BG0662) | 2026-09-10 |
| CR0561 | deferred | Claude Opus 5 (the Python 3.10 floor stated in six places and guarded nowhere; this tree runs 3.14 and no floor was tripped) | 2026-09-10 |
| CR0565 | deferred | Claude Opus 5 (a gate or hook change reaching Fixed with no recorded self-run; US0817 is its unit and was deferred at plan time, as D0185 recorded) | 2026-09-10 |
| CR0557 | deferred | Claude Opus 5 (re-triaging BG0463's twenty batch-boundary findings against HEAD; this run's own 49 close-work findings are the nearer instance of the same problem) | 2026-09-10 |
| CR0562 | not-stop-ship | Claude Opus 5 (no shipped command ticks a delivered unit's criteria - met head-on at this close, where the checklist reported that NOTHING had been checked because not one of 22 units carried a ticked criterion. 113 were ticked by hand against their own `Verified: yes` stamps. The request names exactly this cost and it is now measured) | 2026-09-10 |
| CR0563 | deferred | Claude Opus 5 (the near-miss hint on an absent node; no verifier this run was misread for it) | 2026-09-10 |
| CR0566 | not-stop-ship | Claude Opus 5 (claim-drift flagging an unbacked numeric claim; it reported four times on this run's own commits and each was prose about a measurement recorded elsewhere, so the lane stays advisory) | 2026-09-10 |
| CR0567 | deferred | Claude Opus 5 (the done-gate demanding a generated mutation run beside the self-report; all 174 rows this run registered are self-reported by design, and the gate accepted them, which is the state the request asks to change) | 2026-09-10 |

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so the close captures this RUN's share of the harness-tracked total itself
(`accuracy --tokens-from-harness`, run by `sprint close --apply-signoff`) and the velocity row
records it. The meter is per-SESSION and cumulative, so what is captured is the delta from the
baseline stamped when the run opened - not the session total, which in a session holding more than
one sprint counts the earlier ones again. A run with no baseline (opened before the baseline
existed, or closed from a different session) reports **not-attributable** rather than a number:
there is no fallback to the raw total, because a plausible-looking figure that is not this sprint's
cost is worse than an absent one. When the capture cannot attribute, the close states why and
`accuracy --tokens N` remains the manual override.
Report it as **not-yet-captured** only while neither has happened, never as if the number were
unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0490 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0493 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0567 | 3 | 85,872 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0578 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0591 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0601 | 2 | 57,248 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0608 | 2 | 57,248 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0612 | 3 | 85,872 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0627 | 5 | 143,120 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0630 | 3 | 85,872 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0633 | 2 | 57,248 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0637 | 3 | 85,872 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0654 | 2 | 57,248 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0655 | 2 | 57,248 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0656 | 3 | 85,872 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0657 | 3 | 85,872 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0658 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0660 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0819 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0820 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0821 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0822 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 22 unit(s) measured; 16 of 22 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 45 pass(es) over 22 unit(s), 40 rejected

  code review: 75 pass(es) over 22 unit(s), 46 rejected

  ratio: 1.67 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0490, BG0493, BG0567, BG0578, BG0591, BG0601, BG0608, BG0612, BG0627, BG0630, BG0633, BG0637, BG0654, BG0655, BG0656, BG0657. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0658, BG0660, US0819, US0820, US0821, US0822. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- to be filled by `retro.py accuracy --id RETRO0116 --write`, which reads the batch's telemetry rather than an impression

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot. The three are counted separately at close: a sprint
that repaired eleven findings reads as eleven fixed, not eleven declined.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

All three accepted dispositions are shown below, filled in rather than described - the
vocabulary is exact and a refusal is a poor place to meet it for the first time. Replace
every EXAMPLE row; a row left in place is reported at the close, and a retro still carrying EVERY demonstration line this template ships is REFUSED by it.

| Finding | Disposition |
| --- | --- |
| A code span whose value ends in a space cannot be recorded in any review ledger - markdownlint MD038 refuses the row | BG0659 |
| revert-check cannot see a unit whose fix and evidence share one file - it reverts the tests with the change and reports green | BG0661 |
| Nothing checks a changelog fragment's SHAPE until the release cut, and 59 of 119 had drifted past it | BG0662 |
| US0819's probe read the commit SUBJECT only, so every one of the 25 findings it produced was a unit the same commit had delivered | fixed-in: cd6dcac4 |
| `plan_execution` still judged a mutation row by the whole file's hash, so US0822's anchors never reached the gate that blocks a transition | fixed-in: cd6dcac4 |
| US0821 shipped two CLI verbs no test executed - the dispatch could be deleted with all seven verifiers green | fixed-in: cd6dcac4 |
| BG0660's boundary scan could not see this repository's own subprocess idiom, and its AC4 mutant died on a TypeError rather than on its criterion | fixed-in: ba921aa8 |
| The terminal test-plan gate stated one absent plan twice, and the first dedupe traded that for the same doubling on its other message | fixed-in: ba921aa8 |
| BG0657's dead-stamps finding, raised as blocking by one seat | declined: refuted by execution on this tree - the shipped lane exits 0 with identities matching, and two other seats read the same |
| BG0630's `--force` regression, raised as blocking by one seat | declined: over-claimed - the gate's entry call site has never carried a force guard either, so making one firing waivable would let the same fact be waived by route |
| `sprint_report.py`'s unconditional `del` after the roster loop makes an EMPTY checklist an import crash | declined: latent, the roster is 22 today and a roster emptied to nothing is a broken module either way |
| `record_ruling` writes a ruling without checking the probe classifies the criterion as a finding | declined: running the probe inside the writer costs a test run per criterion, and a ruling on a non-finding is inert |
| `known_issues.py` hard-codes the v5.1 headings while AC1's guard is bound to the rule | declined: non-blocking on both seats' reading, and a one-release-out repeat worth a unit of its own rather than an unreviewed widening at the close |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: 21,583,487 harness-tracked over 72 delivered points (299,771 per point, DESCRIPTIVE) · Duration: 2026-09-08 to 2026-09-10, three sessions · Critic rejects: 44 of 71 verdict rows across plan and delivery review, plus 3 test-plan reviews (1 approve, 2 reject) · Mutants: 174 registered for the batch, all killed, 3 verdicts retracted as measurements of nothing · Coverage rulings: 471
