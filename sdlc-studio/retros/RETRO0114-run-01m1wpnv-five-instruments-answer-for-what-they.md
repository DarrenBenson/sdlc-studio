# RETRO-0114: RUN-01M1WPNV: five instruments answer for what they measured

> **Date:** 2026-09-07
> **Batch:** BG0651, BG0646, BG0649, BG0645, BG0648
> **Goal:** Five instruments answer for what they measured, not for what happened to be in front of them (D0182)
> **Delivered:** 5 / 5   **Blocked:** 0

## Delivered

- BG0651 (5 pts, 0b9f4e12) - the mutation ledger keeps another unit's rows and marks them stale at register, and the pre-commit `evidence-drift` lane refuses a commit that drifts a delivered unit's rows, naming the unit, the file, the rows and the remedy.
- BG0646 (5 pts, f6f34865) - `status.py` answers this corpus in under a second, headline first from the run record, the census and every advisory inside one corpus sweep reading each file once; the run line's count comes from `handoff._classify`, the one predicate `build` reads too.
- BG0649 (3 pts, ea8a99a0) - `test_critic` imports what it uses, and the `module-alone` boundary lane runs every skill test module alone under unittest from the repository root in parallel with the `serial_only` partition after, refusing a partition it cannot read; measured green on this repository at four to five minutes.
- BG0645 (2 pts, 7d58b1ce) - a plan-review rejoinder keeps the plan-review shape, both rejoinders print a fingerprint footer, and the rejoinder's fingerprint identifies its base brief and phase so `record --brief` recognises it.
- BG0648 (5 pts, 72e7ab71) - a criterion outside `## Acceptance Criteria` is an error naming the heading, is neither run nor briefed, and is named by lint; the two corpus offenders moved into their section.

## Blocked / deferred

- Nothing in the batch. Five tooling CRs (CR0564 to CR0568) and eleven Lows in CR0511 were filed from the review rounds rather than pulled in.

## What went well

- The seats caught every real defect before it shipped: a boundary lane red on this repository (BG0649 r1, all three seats), a count pinned by a prefix match over a fixture that reached two of five branches (BG0646 r1), a rejoinder fingerprint nothing could reproduce (BG0645 r1). Each was demonstrated by execution, none by impression.
- The evidence-drift lane shipped first (BG0651) and then guarded the other four: every later edit to a shared file was refused until the drifted rows were re-measured, which is the LL0053 hole closed.
- The operator's question - why do reviews keep failing - produced a root-cause analysis in the session, a memory note, and five filed CRs, and the last unit shipped with the new pre-review checks done by hand: the shipped command run on this repository before briefing, one mutant per new branch, no unmeasured number.

## What was hard / what stalled

- Twelve REJECTs across the four reviewed units before BG0648 (3, 2, 5, 2), eleven review rounds, each round twenty to thirty minutes across three seats. Every rejection was something the author could have found in minutes: the real-target run, a measured number, a mutant for a branch the fixture never reached.
- The mutation ledger's byte-keyed rows cost more wall-clock than the code: every edit to gate.py, status.py, critic.py, AGENTS.md or the pre-push hook drifted earlier units' rows (BG0615, BG0617, BG0619, BG0631, BG0640, BG0641, BG0642, BG0647, BG0523, BG0543, BG0603, BG0643), each re-applied by hand from its description; two of those re-applications found rows that had become equivalent.
- Commit hooks at twelve to fifteen minutes each, twice refused on paperwork (provenance ids in comments, the disclosure count); the harness killed four background waiters on a false low-memory signal.

## Lessons

- Fixture-green is not real-target-green: a gate lane, a hook or a command must be run where the hook runs it, on this repository, before a brief is rendered; the environment differences (a relative versus absolute PYTHONPATH) live only there.
- A number in prose needs the command that produced it beside it; a figure copied from a budget constant or an old bug report shipped twice and was refuted by measurement both times.
- Mutants come from the delivered code's branches, not only from the plan table: every survivor a seat found sat on a branch the unit's own selectors never executed.
- A structural pin beats a string: the worker count printed from the pool survived; the sleepers' own overlap did not.
- When the build departs from the plan-reviewed design, amend the criterion before the brief renders, or the seat judges the code against a law it no longer meets.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Run the shipped command on THIS repository before briefing, and record its figure in the revision row.
- One mutant per new branch from the diff, not only the plan's rows; a clause with no fixture case reaching it is unpinned.
- Every number in a criterion, fragment or roster carries its measuring command.
- Register mutation evidence after the LAST edit, and expect every shared-file edit to drift other units' rows (LL0053).
- Amend the criterion when the design moves, with a revision row, before the brief renders.

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
| BG0490 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, four bug repairs are Fixed with half their title undelivered and no recorded narrowing; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0493 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, four more verifiers pass on a delivery that has been made inert; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0567 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, the upgrading-project baseline compares against this tree minus one branch, not against th; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0578 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, test-file attribution is decided by name frequency, so mentioning one more module silently; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0591 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, status and close_owed give opposite answers about the same units; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0601 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, The dry-run class sweep compares only the first two probes of each pair; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0608 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, The budget line still LEADS with the seconds comparison BG0594 proved uninformative, so th; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0612 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, Three limbs that survived the closure of BG0599 and BG0602: an edit-verb gap, an unpinned ; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0614 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, the mutation ledger keeps several LIVE rows on one (unit, criterion, row) key, and the joi; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0627 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, eleven other fields-file consumers carry the same `or ""` guard, so a falsey value is repo; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0630 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, the test-plan gate is skipped on In Progress to Done, so a unit that entered before its re; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0633 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, transition.py annotate is a THIRD writer of Severity and carries no vocabulary, so the cla; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0637 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, critic._clean escapes underscores INSIDE code spans, corrupting 655 identifiers across the; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0638 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, five sprint-checklist rows state a conclusion they never established, and _ck_known_issues; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| BG0652 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, status.py hint takes 56 seconds on this corpus: its close-owed advisory runs outside any c; disclosed against v5.1 under D0136 to D0139 | 2026-09-07 |
| CR0511 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - the consolidated Lows, eleven added this run, none a blocker | 2026-09-07 |
| CR0564 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - coverage of new lines by the unit's own verifiers - a gate to build, not a defect | 2026-09-07 |
| CR0565 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a recorded self-run for gate-lane changes - a gate to build | 2026-09-07 |
| CR0566 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - numeric claims without a measurement - an advisory lane to build | 2026-09-07 |
| CR0567 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a generated mutation run demanded at the done-gate - a gate to build | 2026-09-07 |
| CR0568 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - register replaces a duplicate live row - a small fix, not a blocker | 2026-09-07 |
| CR0424 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - sprint close requires an RV artifact plus review_prep stamp | 2026-09-07 |
| CR0441 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - In-flight sprint controls: capacity-aware swap, bulk add by | 2026-09-07 |
| CR0496 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - A project-config decision is invisible to the forward-port c | 2026-09-07 |
| CR0497 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - The v5 upgrade grandfathers a project's history silently, so | 2026-09-07 |
| CR0499 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - A sprint is never asked whether it produced a SHIPPABLE incr | 2026-09-07 |
| CR0503 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - an adversarial review can be run outside the seat ceremony, | 2026-09-07 |
| CR0504 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - closing review is doing the work development should have don | 2026-09-07 |
| CR0507 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - closing a sprint asks twenty questions when it should ask tw | 2026-09-07 |
| CR0512 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - A unit review is scoped to that unit's own diff and blocks o | 2026-09-07 |
| CR0515 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - An agent customises content, never tooling: hand-rolled work | 2026-09-07 |
| CR0526 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - a sprint ends with nothing open - a non-stop-ship finding be | 2026-09-07 |
| CR0546 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - the run should notice work it delivered that its batch never | 2026-09-07 |
| CR0547 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - verify_ac revert-check: revert a unit's production files and | 2026-09-07 |
| CR0548 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - derive `Verification depth` from the ledger instead of autho | 2026-09-07 |
| CR0550 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - The test-plan gate is scoped by DATE alone, so it cannot be | 2026-09-07 |
| CR0551 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - The appetite ceiling measures WALL-CLOCK since the run opene | 2026-09-07 |
| CR0552 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - revert-check mutates the live working tree, so a boundary ga | 2026-09-07 |
| CR0553 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - The exemption reason floor counts characters, so twelve junk | 2026-09-07 |
| CR0554 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - A plan row whose recorded kill node is not the criterion's o | 2026-09-07 |
| CR0555 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - The expensive half of the test-plan gate fires before a diff | 2026-09-07 |
| CR0556 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - A bug reaches a terminal status with no independent judgemen | 2026-09-07 |
| CR0558 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - the derived-depth lane checks each span against its own seal | 2026-09-07 |
| CR0559 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - the same concept is named three ways across the toolchain an | 2026-09-07 |
| CR0560 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - filing a finding leaves the disclosure page stale, so the tr | 2026-09-07 |
| CR0561 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run (In Progress) - the declared Python 3.10 floor is stated in six shipped plac | 2026-09-07 |
| CR0523 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - the unreviewed span is reported DURING the run, not discovered at the | 2026-09-07 |
| CR0524 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - a review verdict separates a broken feature from evidence that cannot | 2026-09-07 |
| CR0540 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - Low-severity crs (consolidated) | 2026-09-07 |
| CR0543 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - plan_review has no adoption cutoff, so the one hard risk-proportional | 2026-09-07 |
| CR0544 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - Nothing reviews a REPAIR's approach or a PROCEDURE's plan before it is | 2026-09-07 |
| CR0545 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - Everything after the tag is un-tooled: no command publishes a release, | 2026-09-07 |
| CR0557 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - BG0463's twenty batch-boundary findings need re-triage against HEAD be | 2026-09-07 |
| CR0562 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - no shipped command ticks a delivered unit's acceptance criteria, so th | 2026-09-07 |
| CR0563 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - verify_ac run prints the near-miss hint when a collected file's node i | 2026-09-07 |
| RFC0056 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a design exploration, not a defect; not decomposed into this run - Keep the TRD and TSD true: mechanical claim-drift detection and a cons | 2026-09-07 |
| RFC0057 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a design exploration, not a defect; not decomposed into this run - A queue of planned sprints, so the planner and the runner can be diffe | 2026-09-07 |
| CR0509 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0528 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0529 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0530 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0531 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0533 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0534 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0535 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0536 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |
| CR0539 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-07 |

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
| BG0651 | 3 | 97,071 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0646 | 3 | 97,071 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0649 | 1 | 32,357 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0645 | 2 | 64,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0648 | 3 | 97,071 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 5 unit(s) measured; 5 of 5 forecast at plan time.**

**Sprint tokens/point: 280,881** (6,460,265 tokens over 23 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 1.58 points/elapsed-hour** (23 points ACCEPTED over 14.517h, run-state - a CALENDAR SPAN with no idle deducted, since the run recorded no gap; it is not working time, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing

  code review: 30 pass(es) over 5 unit(s), 13 rejected
Unmeasured: BG0651, BG0646, BG0649, BG0645, BG0648. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- No unit is rated this run: per-unit actuals were not captured while the units were delivered, so the forecast rows in `retros/evidence/forecasts-2026-09-07.jsonl` stand unmeasured. What the wall clock says without the ratio: the 23-point batch took one session of roughly fourteen hours, most of it in eleven review rounds and the ledger re-measures they forced, against a plan appetite the goal review sized for one round per unit.

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
| status.py hint still costs 56 s outside any sweep | BG0652 |
| new lines a unit's own verifiers never execute are not refused at Fixed | CR0564 |
| a change to a gate lane or hook reaches Fixed with no recorded run on the repository | CR0565 |
| a numeric claim in prose ships with no measurement behind it | CR0566 |
| the done-gate reads self-reported mutant rows only, never a generated run | CR0567 |
| mutation.py register appends a duplicate live row instead of replacing it | CR0568 |
| verify_ac depth reads a class selector as undetermined | CR0511 (Low) |
| handoff.build raises on a loop-state entry with no attempts key | CR0511 (Low) |
| the dashboard's other advisories still re-read files past the sweep | CR0511 (Low) |
| read_text_safe serves stale text for a file written inside an open sweep | CR0511 (Low) |
| test_gate prints 24 JSON lines under the unittest runner | CR0511 (Low) |
| the importability census is red at the base ref for a missing markdownlint | CR0511 (Low) |
| the gate compares a boundary run to the 45 s per-commit budget | CR0511 (Low) |
| the delivery brief's footer prints a record command that does not run as printed | CR0511 (Low) |
| record noted an unrecognised brief for every rejoinder fingerprint | fixed-in: 7d58b1ce |
| the module-alone lane exported an absolute PYTHONPATH and was red on this repository | fixed-in: ea8a99a0 |
| the run line's count was a second copy of handoff's predicate pinned by a prefix match | fixed-in: f6f34865 |
| BG0631's AC5 guard became equivalent once the parser filtered the header row | fixed-in: 7d58b1ce (ruled equivalent in the ledger) |
| BG0641's AC4 prose counts two boundary lanes where the hook now names three | declined: the pin is intact and re-measured, the count is stale by one and recorded in BG0641's revision row |
| the rejoinder fingerprint does not bind the prior verdict or the round | declined: disclosed in the fragment, base brief and phase are what a matcher can reproduce |

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

- Tokens: captured at close from the harness delta · Duration: 01:01Z to close, one session · Critic rejects: 13 of 30 seat verdicts (BG0651 3, BG0646 2, BG0649 5, BG0645 2, BG0648 1), every one repaired

## Handoff

- [HO-0068](../handoffs/HO0068-five-instruments-answer-for-what-they-measured-not.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
