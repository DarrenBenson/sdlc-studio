# RETRO-0106: Six instruments repaired, and three of them were not delivered when I first ticked them

> **Date:** 2026-08-20
> **Batch:** BG0593, BG0594, BG0595, BG0596, BG0597, BG0598
> **Goal:** Every instrument this run touches reports only a verdict its own recorded evidence supports, and refuses rather than softens when the evidence is not there.
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

- BG0593 (5pt) - `close --dry-run` previewed against a scratch holding only `sdlc-studio/`, so every
  probe reading `.git`, `.claude/skills/`, `tools/` or `changelog.d/` degraded to a softer verdict
  than the close it previews. A read root now travels beside a pure copy, reaching only steps whose
  signature accepts one; and `_changed_paths` reports a tree with NO COMMITS distinctly from a diff
  it could not read, because the remedies are opposite and the message was one.
- BG0594 (3pt) - the budget lane judged one row of a width-varying series against one scalar, and
  judged a ~899s full run against a 380s per-commit ceiling. The verdict is now taken on the per-test
  RATE against a ceiling declared as a rate, the full suite has its own ceiling, and the close and
  release boundaries are priced from the full series rather than from whatever the last commit ran.
- BG0595 (3pt) - one hook test ran against the real repository, consumed the gate handoff a real
  commit was going to use, and started a full skill suite inside a unit test. The hook now exits
  before the suite lanes when handed no message file, keyed on the ABSENT MESSAGE and never on the
  identity of the caller.
- BG0596 (5pt) - `_testplan_rows` keyed by criterion, so a plan declaring several mutants for one AC
  kept one and `--from-plan` printed `every one executed and killed` over mutants it had never
  joined. The join is keyed `(criterion, row)`, the done-gate names the unexecuted row and quotes
  its mutant, and the shipped brief and help page no longer teach a format the tool accepts.
- BG0597 (3pt) - `testplan derive` silently destroyed an authored row at exit 0 when a criterion
  carried two, and dropped an ORPHAN row the same way. It preserves every row in file order and
  REFUSES rather than losing one.
- BG0598 (2pt) - the forecast's BUILT-NOT-CLOSED exclusion read verifier greens and never the verdict
  ledger, so a unit rejected four times was priced at zero under a sentence ending `close them`. The
  read spans BOTH ledgers and a rejected unit gets its own class, priced IN.

## Blocked / deferred

- Nothing blocked. The batch was re-pointed twice under review - BG0596 3 -> 5 and BG0593 3 -> 5 -
  because two units' declared `Affects` understated the surface their criteria actually needed.

## What went well

- **The gates did the work I could not.** Eleven refusals across the run, every one a real
  inconsistency: a release note claiming four open High findings while the corpus held six, a
  disclosure page stale the moment two bugs were filed, a derived index that moved when a unit was
  re-pointed, ten internal bug ids in shipped `scripts/`, an unconfined git call, two criteria
  sharing one verifier, and a ledger that dropped five registrations because I had edited the file
  after recording them.
- **The verify-ratchet found a non-delivery nothing else could.** It refuses any NEW pair of criteria
  sharing one selector, on the ground that two ACs sharing a selector cannot both discriminate.
  Forced to give BG0594 AC6 its own test, the fact that `full_gate_seconds` had never been fixed
  surfaced in one run - its mutant had been applied to the call site and read KILLED throughout.
- **Panel sign-off worked.** `critic signoff --panel` refused two malformed attempts and taught the
  correct form each time: the signer is read from the run's recorded assignment, never named at
  signing time.

## What was hard / what stalled

- **Five plan-review rounds and three delivery-review rounds.** Every round found something real and
  the counts fell - 16, 5, 3, 2 on the plan; then non-delivery, four bad verifiers, and a moved
  probe on delivery - but the ceremony cost more than the fixing, and that ratio is mine, not the
  process's.
- **Three of six units were NOT DELIVERED when I first ticked them.** BG0593's tests rebuilt the
  production construction in a private helper, so deleting the entire change left 916 tests green.
  BG0594's rate verdict was never written; `over` was still `measured > budget` and reverting it
  survived all 53 tests in the file. BG0596 AC7's refusal branch printed nothing.
- **Eight of thirty-four mutants recorded as killed did not die on the test their criterion named.**
  My `--from-plan` greens were replaying verdicts I had typed, not executions.
- **The defect relocated in every single round.** An equivalent mutant moved from BG0596 AC6 to
  BG0593 AC4; a duplicate pair moved from BG0595 AC3/AC5 to AC1/AC3; the scratch degradation moved
  from the tick row to `_ck_doc_surface`. A repair judged only against its own finding is how.
- **Two of my own filings carried false premises**, BG0595's twice, and both corrections came from
  running the thing rather than reading it.
- **My own revert check destroyed uncommitted work** on its first run - it stashed the tree and
  restored production files from HEAD, discarding every edit since the last commit.

## Lessons

- **A test and its mutant authored together share one mental model, so they agree with each other and
  not with the code.** Apply the mutant FIRST, against the unmodified tree, and confirm the named
  test is red before writing a line of it. Promoted as LL0054.
- **Every assertion that a thing works needs its twin in the state where it must not.** Four
  successive cuts of one test here passed against a row that had never reached the code under test -
  `no base ref`, `no git history here`, `no ticked criteria found` - and the paired control caught
  all three. An assertion about success alone cannot tell a working mechanism from one that never ran.
- **Killing a mutant one construct away from the defect proves nothing about the construct behind
  it.** BG0594 AC6's mutant hit the call site while the function still returned the wrong series, and
  the ledger recorded it killed.
- **A criterion's derived Test Plan is derived output.** Rewriting criteria and leaving the table is
  the same class as hand-editing `_index.md`: BG0593's rows described a mechanism the redesign had
  removed, and its own `testplan derive` refused the artefact.
- **A fixture that supplies BOTH sides of a distinction cannot show it.** BG0598's fixture wrote both
  ledgers, so a single-ledger read still found the verdict and the mutant survived; it now writes the
  batch ledger alone and asserts the other does not exist.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Apply the mutant FIRST, against the unmodified tree, and confirm the named test is red before writing a line of it. A test and its mutant authored together share one mental model.
- Every assertion that a thing works needs its twin in the state where it must not. Success alone cannot tell a working mechanism from one that never ran.
- Killing a mutant one construct away from the defect proves nothing about the construct behind it.
- A criterion's Test Plan is DERIVED output: rewrite the criteria and the table goes stale, exactly as a hand-edited index does.
- A fixture that supplies both sides of a distinction cannot show it.

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
| BG0463 | not-stop-ship | authoring session | 2026-08-20 |
| BG0490 | not-stop-ship | authoring session | 2026-08-20 |
| BG0493 | not-stop-ship | authoring session | 2026-08-20 |
| BG0567 | not-stop-ship | authoring session | 2026-08-20 |
| BG0578 | not-stop-ship | authoring session | 2026-08-20 |
| BG0581 | not-stop-ship | authoring session | 2026-08-20 |
| BG0586 | not-stop-ship | authoring session | 2026-08-20 |
| BG0587 | not-stop-ship | authoring session | 2026-08-20 |
| BG0588 | not-stop-ship | authoring session | 2026-08-20 |
| BG0591 | not-stop-ship | authoring session | 2026-08-20 |
| BG0592 | not-stop-ship | authoring session | 2026-08-20 |
| BG0593 | not-stop-ship | authoring session | 2026-08-20 |
| BG0594 | not-stop-ship | authoring session | 2026-08-20 |
| BG0595 | not-stop-ship | authoring session | 2026-08-20 |
| BG0596 | not-stop-ship | authoring session | 2026-08-20 |
| BG0597 | not-stop-ship | authoring session | 2026-08-20 |
| BG0598 | not-stop-ship | authoring session | 2026-08-20 |
| BG0599 | not-stop-ship | authoring session | 2026-08-20 |
| BG0600 | not-stop-ship | authoring session | 2026-08-20 |
| CR0496 | not-stop-ship | authoring session | 2026-08-20 |
| CR0497 | not-stop-ship | authoring session | 2026-08-20 |
| CR0499 | not-stop-ship | authoring session | 2026-08-20 |
| CR0503 | not-stop-ship | authoring session | 2026-08-20 |
| CR0504 | not-stop-ship | authoring session | 2026-08-20 |
| CR0507 | not-stop-ship | authoring session | 2026-08-20 |
| CR0509 | not-stop-ship | authoring session | 2026-08-20 |
| CR0511 | not-stop-ship | authoring session | 2026-08-20 |
| CR0523 | not-stop-ship | authoring session | 2026-08-20 |
| CR0524 | not-stop-ship | authoring session | 2026-08-20 |
| CR0528 | not-stop-ship | authoring session | 2026-08-20 |
| CR0529 | not-stop-ship | authoring session | 2026-08-20 |
| CR0530 | not-stop-ship | authoring session | 2026-08-20 |
| CR0531 | not-stop-ship | authoring session | 2026-08-20 |
| CR0533 | not-stop-ship | authoring session | 2026-08-20 |
| CR0534 | not-stop-ship | authoring session | 2026-08-20 |
| CR0536 | not-stop-ship | authoring session | 2026-08-20 |
| CR0539 | not-stop-ship | authoring session | 2026-08-20 |
| CR0540 | not-stop-ship | authoring session | 2026-08-20 |
| CR0543 | not-stop-ship | authoring session | 2026-08-20 |
| CR0544 | not-stop-ship | authoring session | 2026-08-20 |
| CR0545 | not-stop-ship | authoring session | 2026-08-20 |
| CR0546 | not-stop-ship | authoring session | 2026-08-20 |
| CR0547 | not-stop-ship | authoring session | 2026-08-20 |
| CR0548 | not-stop-ship | authoring session | 2026-08-20 |

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
| BG0593 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0594 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0595 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0596 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0597 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0598 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 6 unit(s) measured; 6 of 6 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 31 pass(es) over 6 unit(s), 25 rejected

  code review: 6 pass(es) over 6 unit(s), 6 rejected

  ratio: 0.19 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0593, BG0594, BG0595, BG0596, BG0597, BG0598. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The points were re-pointed UPWARD twice under review - BG0596 3 -> 5 and BG0593 3 -> 5 - and both
  times because the unit's declared `Affects` understated the surface its criteria needed. The
  estimate did not miss the build; it missed the SCOPE, and the review found it rather than the
  planner. The real overrun is not in the points at all: it is eight review rounds against a
  21-point batch, and every one of them found something, which means the forecast was right about
  the work and wrong about the rework.

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
| `testplan derive` reports one row fault per invocation while computing all four - 22 round trips to clear 33 rows | BG0599 filed |
| The `unnameable` exemption is itself held to the four mutant rules, so an honest declaration is refused unless it names a file and a verb it does not mean | BG0600 filed |
| Nothing asks whether a fix would be MISSED if it vanished - the check that found this batch's worst defect | CR0547 filed |
| `Verification depth` is prose an author types, and it was false on five of six units in this batch | CR0548 filed |
| Eight of thirty-four mutants recorded as killed did not die on their own criterion's test | fixed-in: 11ecb400 |
| A test and its mutant authored together share one mental model | LL0054 filed (global) |
| My own revert check stashed the tree and restored production files from HEAD, destroying every uncommitted edit | fixed-in: it now snapshots bytes and restores those |
| `review_rounds_across_ledgers` sorts by a day-granularity date string, so two verdicts on one day are ordered by ledger rather than by clock | declined: real, but it decides `rounds[-1]` only when a unit gets two verdicts in two ledgers on the same day, and the fix is a timestamp migration across both files - out of scope for a batch about instrument honesty, and no unit here hit it |

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

- Plan-review rounds: 5 (4 REJECT, 1 APPROVE) · Delivery-review rounds: 3 · Criteria: 34 ·
  Declared mutants: 34, every one killed by its own criterion's named test · Units red on revert:
  6/6 · Suite at close: 6,656 passed · Gate refusals, all real: 11 · Findings filed during the run:
  BG0597, BG0598, BG0599, BG0600, CR0547, CR0548, LL0054
