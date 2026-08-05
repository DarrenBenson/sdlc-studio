# RETRO-0094: Every verdict this repo's gate writes can be trusted and read: a collapsed suite leaves no reusable green, a red runner names the test that failed, the close-owed headline agrees with its own exit code, and the charter queue is inspectable during a run and consumed at the end of one. With the instruments honest, the debt the v5 scope caps baselined is paid: the run lifecycle documented in the form the parser accepts, validate ratcheting its warnings rather than accumulating them, and the duplicate Verify groups split into selectors that can discriminate

> **Date:** 2026-08-05
> **Batch:** BG0507, BG0513, BG0500, BG0514, BG0515, BG0518
> **Goal:** Every verdict this repo's gate writes can be trusted and read: a collapsed suite leaves no reusable green, a red runner names the test that failed, the close-owed headline agrees with its own exit code, and the charter queue is inspectable during a run and consumed at the end of one. With the instruments honest, the debt the v5 scope caps baselined is paid: the run lifecycle documented in the form the parser accepts, validate ratcheting its warnings rather than accumulating them, and the duplicate Verify groups split into selectors that can discriminate.
> **Delivered:** {{n_done}} / {{n_total}}   **Blocked:** {{n_blocked}}

## Delivered

Six units reached terminal. Four more shipped their code and sit at Review, because
`review.two_role_after` will not let a run count a story the authoring session signed.

- BG0513 - a red suite leg names its failing test and keeps a per-run log tied to its own
  verdict. Delivered NARROWED; BG0519 carries the unattributed 4.5x slowdown.
- BG0507 - a collapsed suite leaves no reusable green. Third door into one fail-open.
- BG0518 - `close_owed`'s headline and its exit code derive from one predicate.
- BG0514 - `queue show` is readable during a run, which is the only time it is used.
- BG0515 - the charter queue has an exit; `plan --write --charter` spends it.
- BG0500 - the runbook guard runs in a lane, not only in the tools suite.

Code shipped, awaiting sign-off at Review: US0468, US0480, US0481, US0637.
BG0463 delivered narrowed and stays Open with its residue named.

## Blocked / deferred

Fifteen units descoped to the backlog by `sprint call`, none started. EP0207's six were added
mid-run at the operator's direction and never begun - they lead the next run. BG0406, BG0421,
US0635 and US0636 were verified as genuinely blocked rather than merely unattempted: BG0406's
smallest coherent slice reaches `children_of`, which decides status across 900+ artefacts;
BG0421 needs 21 design rulings that belong to the operator; US0635/0636 need 20 new
discriminating tests and are all-or-nothing on their first criterion.

## What went well

The independent pass did exactly what it exists for. Ten units passed every automated gate -
full suite, `verify_ac`, lane-check, mutation as the author ran it - and two independent seats,
briefed with the shipped tool, both REJECTed on 11 findings and produced IDENTICAL unit-level
splits. Convergence between two reviewers who never spoke is what makes the verdict evidence
rather than one reviewer's disposition.

The instrument built first paid for itself inside the run. BG0513's log preservation named the
failing tests on the first real red the suite produced, which is what five earlier invocations
could not do.

## What was hard / what stalled

The finding rate. Ten units delivered produced eight filed findings. Under `review.policy:
block` that is a treadmill: every run's review generates roughly what the run closed, so the
backlog cannot converge however fast anyone works. D0129 adopts carry-forward as the interim
answer and names CR0510 and EP0207 as the real ones.

Ceremony cost is flat regardless of blast radius. A help-page rewrite received the same
two-seat adversarial review as a change to the commit hook. That is CR0510, still Proposed.

One unit was mispriced by a factor that is worth recording: US0480 was estimated at 5 points and
consumed six full-suite runs, because adding a gate lane fired five separate roster guards in
sequence. Three of those runs found real defects, so the cost was not waste - but no forecast
accounted for it.

## Lessons

- **A mutant derived from the implementation is the mutant the test was built to catch.** Five
  AC-named mutants did not kill their tests, on units committed claiming they had. The generative
  defect was writing each mutant AFTER the code, from the code. The criterion already stated the
  mutant in every case - US0468 AC2 literally says "a key added or renamed fails the test" - and
  the test was written from the implementation instead. Derive the mutant from the criterion
  before the code exists, or the mutation check certifies nothing. (LL0044, L-0272.)
- **Reviewing the test costs two orders of magnitude less than reviewing the code.** Measured
  this run, by accident, on the first hand-run use of EP0207's mechanism: an independent seat
  rejected all three rows of US0629's test plan for 55k tokens and 3 minutes. The batch-boundary
  review that caught the same class - verifiers that cannot fail on what they claim - cost
  roughly 400k tokens and two hours, after the code had shipped.
- **Fixing the instance leaves the class.** BG0500 added `runbook.py` to the AGENTS.md lane
  roster; four commits later the same batch shipped a `warning-ratchet` lane and did not. The
  repair was to derive the roster from the hook, one subtest per lane, so lane fourteen fails
  when it is written rather than when a reviewer notices.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro.

- Derive the mutant from the CRITERION before the code exists. A mutant written afterwards is
  the one the test was built to catch, and it certifies nothing.
- Review the test plan, not the code. Measured here at 55k tokens against roughly 400k for the
  same class of finding after shipping.
- Fixing the instance leaves the class: derive the check's alphabet from the thing it checks.
- A skipping test is worse than no test, because it counts as green.
- Verify the premise before asserting it - twice this run a unit was called intractable without
  being opened, and both times the reading was wrong.

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
| BG0519 | not-stop-ship | BG0513's residue: the tools-leg slowdown is unattributed and the flake unproven absent | 2026-08-04 |
| ID | Ruling | Why | Ruled |
| --- | --- | --- | --- |
| BG0350 | not-stop-ship | 25 Done stories carry no independent critic verdict, waived rather tha - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0406 | not-stop-ship | Three units delivered nothing: BG0372 writes no velocity column, BG035 - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0421 | not-stop-ship | Twenty-one Open Questions reached a terminal status unanswered, and ar - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0457 | not-stop-ship | Four spec-agreement guards pin prose to prose: a set comparison that c - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0463 | not-stop-ship | Twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary revi - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0469 | not-stop-ship | close_owed reports a close that already happened: a unit raised and Fi - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0486 | not-stop-ship | duplicate verifiers are grouped on a normalised string, so two ACs run - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0488 | not-stop-ship | US0608 and US0609 ship a feature no CLI invocation can reach, and thei - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0490 | not-stop-ship | four bug repairs are Fixed with half their title undelivered and no re - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0491 | not-stop-ship | lane-check scans only stories, so 487 bugs are outside the number a bl - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0493 | not-stop-ship | four more verifiers pass on a delivery that has been made inert - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0495 | not-stop-ship | the velocity row understates twice - it counts only accepted points, o - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0497 | not-stop-ship | three units ship a check whose own criterion names the mechanism that  - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0508 | not-stop-ship | the close report's sibling imports sit outside its advisory try, so an - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0509 | not-stop-ship | the close-time-repair split uses day granularity and a global override - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0510 | not-stop-ship | the plan-review ledger has no kind column, so a second pre-code gate w - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0512 | not-stop-ship | batch add-epic and batch swap mutate a live batch without the ungroome - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0516 | not-stop-ship | the close reports a gate refusal it could not attribute, where the gat - pre-existing and unchanged by this run's diff - it was true before fcdfe206 and holds no unit this batch delivered | 2026-08-05 |
| BG0519 | not-stop-ship | the tools leg's remaining slowdown inside the full runner is unattribu - raised by this run's own boundary review or during it; filed, named against its units, and carried under D0129 - tracked work, not a gate on the run that found it | 2026-08-05 |
| BG0520 | not-stop-ship | the triage session cap is a LIFETIME cap: the session key defaults to  - raised by this run's own boundary review or during it; filed, named against its units, and carried under D0129 - tracked work, not a gate on the run that found it | 2026-08-05 |
| BG0521 | not-stop-ship | US0481 ships a config key that does nothing at plan time, and batch ad - a live defect in shipped behaviour, carried under D0129 with its findings filed - highest-priority repair in the next run, and named as such in the retro's actions | 2026-08-05 |
| BG0522 | not-stop-ship | BG0515's fix reproduces BG0515: a charter with an unresolved Open Ques - a live defect in shipped behaviour, carried under D0129 with its findings filed - highest-priority repair in the next run, and named as such in the retro's actions | 2026-08-05 |
| BG0523 | not-stop-ship | Five acceptance criteria are pinned by verifiers that cannot fail on w - raised by this run's own boundary review or during it; filed, named against its units, and carried under D0129 - tracked work, not a gate on the run that found it | 2026-08-05 |
| BG0524 | not-stop-ship | warning-ratchet reports a stale baseline as clean and exits 0, contrad - raised by this run's own boundary review or during it; filed, named against its units, and carried under D0129 - tracked work, not a gate on the run that found it | 2026-08-05 |
| BG0525 | not-stop-ship | US0629 AC2 asks derive to detect a polarity-flipped restatement, which - raised by this run's own boundary review or during it; filed, named against its units, and carried under D0129 - tracked work, not a gate on the run that found it | 2026-08-05 |
| CR0509 | not-stop-ship | a review worktree opens at a stale base - process improvement, not a defect in shipped behaviour | 2026-08-05 |
| CR0510 | not-stop-ship | ceremony proportional to blast radius - the THROUGHPUT fix this run's retro names as the next thing to build; it is the answer to the finding rate, not a blocker on shipping | 2026-08-05 |
| CR0528 | not-stop-ship | the installed copy is only reconciled at a close - mitigated here by forward-porting before the close, and the copy is verified in sync | 2026-08-05 |
| CR0529 | not-stop-ship | the prior-art check is scoped to the reviewer - a review-efficiency improvement, no shipped behaviour depends on it | 2026-08-05 |
| CR0530 | not-stop-ship | the planner reports shared-file clusters rather than the parallelisable fraction - reporting granularity, and this run was sequential regardless | 2026-08-05 |
| CR0531 | not-stop-ship | a charter's scope query cannot express a decomposition - blocks SC0001's materialisation, which is queued and not started, so it holds nothing this run shipped | 2026-08-05 |

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
| BG0507 | 2 | 94,070 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0513 | 3 | 141,105 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0500 | 2 | 94,070 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0514 | 2 | 94,070 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0515 | 3 | 141,105 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0518 | 2 | 94,070 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 6 unit(s) measured; 6 of 6 forecast at plan time.**

**Sprint tokens/point: 353,810** (4,953,336 tokens over 14 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 1.09 points/elapsed-hour** (14 points over 12.893h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0507, BG0513, BG0500, BG0514, BG0515, BG0518. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- {{what the ratio implies - which units the estimate missed, and why}}

## Actions raised

| Finding | Disposition |
| --- | --- |
| `sprint.affects_check` is inert at plan time, and `batch add` writes the unit before it refuses it | filed BG0521 |
| BG0515's fix reproduces BG0515: the terminal Open-Questions gate leaves the run open and the charter Queued | filed BG0522 |
| Five acceptance criteria pinned by verifiers that cannot fail on what they claim | filed BG0523 |
| The warning ratchet reports a stale baseline as clean, and US0480 AC2 contradicts AC4 | filed BG0524 |
| US0629 AC2 asks for a polarity-flipped restatement to be detected, which is not decidable | filed BG0525 |
| Low-severity test debt across BG0507 and BG0513 | filed CR0511 |
| Ceremony costs the same regardless of blast radius - the throughput defect behind the finding rate | declined here: CR0510 already exists and carries it; a second artefact would split the record |
| The AGENTS.md lane roster was missing `validate.py` | fixed-in: e5fa82d5 - the roster is now derived from the hook, one subtest per lane |

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}

## Handoff

- [HO-0049](../handoffs/HO0049-every-verdict-this-repo-s-gate-writes-can.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
