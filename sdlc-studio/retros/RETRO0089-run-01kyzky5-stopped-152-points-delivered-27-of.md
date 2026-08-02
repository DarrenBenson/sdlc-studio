# RETRO-0089: RUN-01KYZKY5 stopped - 152 points delivered, 27 of 38 units rejected on review

> **Date:** 2026-08-02
> **Batch:** BG0438, BG0423, BG0432, BG0433, BG0435, BG0436, BG0448, BG0462, BG0470, BG0476, BG0478, BG0431, BG0434, BG0437, BG0475, BG0483, US0607, BG0359, BG0420, BG0474, US0466, US0470, US0471, US0472, US0473, US0601, US0602, US0606, US0609, US0611, US0615, BG0401, US0598, US0599, US0600, US0603, US0604, US0605, US0608, US0610, US0612, US0613, US0614, BG0487
> **Goal:** complete the sprint
> **Delivered:** 44 / 44   **Blocked:** 0 (45 planned; US0490 and US0492 dropped with recorded reasons, BG0487 filed and fixed in-batch)

## Delivered

All 45 planned units, 152 of 152 points, across 24 commits. Two units were dropped with
recorded reasons (`US0490`, `US0492` - both document a charter queue that does not exist), and
`BG0487` was filed and fixed inside the batch, leaving 44.

Delivered is not the same as accepted. Five independent passes then returned **27 REJECT and
11 APPROVE** over 38 reviewed units, so the run was STOPPED rather than closed: closing it
would have recorded an approval the review withheld.

## Blocked / deferred

Nothing was blocked. 23 delivered units are parked in `Review`, held by review findings
rather than by anything undone. They return cheaply - most need a verifier that can fail, not
a feature.

Filed and carried: `BG0488`-`BG0494`, `CR0523`, `CR0524`, `CR0525`, plus one low-severity
finding consolidated into `CR0511` by the tooling.

## What went well

**The review discriminated, and it discriminated in both directions.** Reviewers reproduced
by execution rather than by impression, and repeatedly withdrew findings after measuring: one
nearly filed "80 of 615 wrongly cleared", re-measured with a corrected regex, found 4, and
withdrew it. Another cleared a suspected laundering path in `_is_cadence_debt` after probing
four vectors and finding none reachable. Eleven units were approved.

**Every finding that was independently re-checked held up.** Zero callers for `close_report`,
`panel_escalation` and `recorded_signoff_panel`; no `--panel` on `critic.py signoff`; six
mirror offenders in the tree `BG0420`'s guard could not see; `LATEST.md` exempted from
claim-drift; the shipped command printing 167 where two surfaces said 178. All verified
directly, none overstated.

**The instruments caught their author.** `run-suite --check` refused a stale verdict I had
already read as current - the exact failure it was built for, firing on the person who built
it. The `NOT FINISHED` warning fired on this retro's own scaffold. The checklist drift guard
caught `sprint appetite` at the gate.

## What was hard / what stalled

**The batch reached 44 units and 25 commits with no independent pass.** `review-batch --open`
exists precisely so a batch is reviewed at its boundary - its own help says a finding is then
delivery work in the batch that caused it rather than close overhead. Zero spans were opened.
The operator noticed, not the tooling: coverage is computed in one place and read at one
moment, the close, when acting on it costs the most. `CR0523`.

**One defect class produced most of the rejections.** A verifier that greps SOURCE TEXT rather
than exercising behaviour, so the feature can be deleted and the test stays green. Ten-plus
instances. `US0608`: reverting the whole feature survives all 390 tests of `test_gate.py`.
`US0609`: deleting its only call site survives all 701 tests of `test_sprint.py`. `BG0401`
shipped this defect inside the bug whose own title is "a grep over source text is not a test
of what the source does".

**`Affects` did not describe the diff on seven units**, `BG0420` with zero overlap. Since
`critic.py brief` derives review scope from `Affects`, those briefs pointed reviewers away
from the code under review - the mechanism trusted to bound scope, fed bad data by its author.

**`lane-check` flagged the failures before any reviewer looked, and shipping continued.** It
reported all seven EP0198 units and both EP0200 units. It is advisory, so it was read as
noise. The rule was available, measured, and did not change behaviour - which is LL0027 with
the number already in hand.

## Lessons

- **A test that asserts the shape of a change cannot fail when the change is deleted.** The
  weakness was not random: it clustered at the end of units, where the feature already worked
  and the test felt like paperwork. `grep -q "NOT FINISHED"` exits 0 against an unreachable
  print; `assertIn("attribute_kill(", src)` is satisfied by the `def` line. Both shipped.
- **Reviewing the test is cheaper than reviewing the code.** This run spent five adversarial
  passes and roughly 800k tokens to discover, after the fact, that ~14 verifiers could not
  fail. A reviewed test plan would have found the same thing before a line of code. The
  `test-spec` artefact type and the name-the-mutant-first rule ALREADY SHIP; the repository
  contains two test specs and this run wrote none. `CR0525`.
- **"Broken" and "unproven" are different facts and want different words.** Roughly 13 of the
  27 rejections were a feature that does not work; roughly 14 were a correct feature with
  evidence that cannot fail. One verdict carried both, so the count read as catastrophe and
  gave no signal about which repairs were urgent. `CR0524`.
- **An advisory detector that fires on the author changes nothing.** `lane-check`'s yield is
  no longer a question: 7 flagged, 6 independently confirmed hollow. That is the number
  `CR0520` asked for.

## Carried lessons

The five to carry into the NEXT batch. A ranking is a fact about the past; this is a decision,
chosen against what this run actually did rather than against citation counts alone.

- **LL0040 - a library test is not a lane test.** This run's largest defect class, roughly 14
  of the 27 rejections, was a verifier that never entered the shipped entry point. One epic
  committed it five times after naming it in its own criteria.
- **LL0027 - when a rule matters, gate it in the command people actually run.** `lane-check`
  flagged all nine hollow units before any reviewer looked and changed nothing, because it was
  advisory. The unreviewed-span rule is only read at the close, which is why a 44-unit batch
  got there with no pass opened.
- **LL0013 - an enumeration silently exempts what it forgot.** Twice this run: a character
  class that could not match a hyphen exempted every hyphenated script from the runbook guard,
  and a directory prefix exempted every review document from claim-drift.
- **LL0008 - a deterministic tool must fail loud, never report success it did not achieve.**
  The `BG0448` oracle accepted a tick from the wrong section, the commit-msg lane records green
  before its last suite runs, and `best_practice_rules.py` returns 0 when its input is absent.
- **LL0010 - validate a defence using the bug it defends against, before shipping it.** Every
  repair in `307ce91d` was followed by re-running the mutant its predecessor survived, and that
  is the only reason those repairs can be claimed rather than hoped.

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
| BG0438 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0423 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0432 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0433 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0435 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0436 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0448 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0462 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0470 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0476 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0478 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0431 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0434 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0437 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0475 | 2 | 91,620 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0483 | 2 | 91,620 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0607 | 2 | 91,620 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0359 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0420 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0474 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0466 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0470 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0471 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0472 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0473 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0601 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0602 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0606 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0609 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0611 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0615 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0401 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0598 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0599 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0600 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0603 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0604 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0605 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0608 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0610 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0612 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0613 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0614 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0487 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 44 unit(s) measured; 43 of 44 forecast at plan time.**

**Velocity: 4.96 points/elapsed-hour** (76 points over 15.312h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0438, BG0423, BG0432, BG0433, BG0435, BG0436, BG0448, BG0462, BG0470, BG0476, BG0478, BG0431, BG0434, BG0437, BG0475, BG0483, US0607, BG0359, BG0420, BG0474, US0466, US0470, US0471, US0472, US0473, US0601, US0602, US0606, US0609, US0611, US0615, BG0401, US0598, US0599, US0600, US0603, US0604, US0605, US0608, US0610, US0612, US0613, US0614. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0487. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The points estimate held: 152 planned, 152 delivered, no unit over its size. What the estimate did not price is REVIEW REPAIR. A point measured delivery only, so a batch that delivered exactly to forecast still could not be accepted, and the 90 points now sitting in Review are work the forecast never saw. Until CR0525 moves verification before the code, an estimate should be read as the cost of writing it, not the cost of shipping it.

## Actions raised

| Finding | Disposition |
| --- | --- |
| A unit's test plan is not written or reviewed before its code, so a verifier that cannot fail is only found after the code exists | filed: CR0525 |
| One verdict word carries both a broken feature and a correct feature whose evidence cannot fail | filed: CR0524 |
| A 44-unit span reached the close with no independent pass, because coverage is only read at the close | filed: CR0523 |
| US0608 and US0609 ship a feature no CLI invocation can reach, and their tests survive its deletion | filed: BG0488 |
| The commit-msg suite verdict is written before the tool-tests lane, so a green verdict survives its failure | filed: BG0489 |
| Four bug repairs are Fixed with half their title undelivered and no recorded narrowing | filed: BG0490 |
| lane-check scans only stories, so 487 bugs sit outside the yield a blocking decision rests on | filed: BG0491 |
| The suite verdict binds to the commit rather than the tree, and --check ignores which suite ran | filed: BG0492 |
| Four more verifiers pass on a delivery that has been made inert | filed: BG0493 |
| resolve_affects lets a consuming project's file shadow the skill's | filed: BG0494 |
| lane-check missed lane entry made through a shared test helper | fixed-in: 307ce91d |
| The BG0448 terminal oracle was bypassable by a tick or Verify line outside the criteria | fixed-in: 307ce91d |
| EP0198's panel sign-off was unreachable from any shipped command | fixed-in: 307ce91d |
| BG0420's mirror guard scanned the one directory with nothing to find | fixed-in: 307ce91d |
| BG0483 exempted every review document from the claim-drift lane | fixed-in: 307ce91d |
| The runbook guard missed hyphenated scripts, verb rot, step order and commandless steps | fixed-in: 307ce91d |
| Eight verifiers asserted source text rather than behaviour | fixed-in: 307ce91d |
| Three measured claims were false or unsupported in shipped surfaces | fixed-in: 307ce91d |
| Five units declared Affects paths their own diffs never touched | fixed-in: 307ce91d |
| The suite-claim lane fires on a message that quotes a greenness claim | filed: CR0511 |
| sprint stop stamps the outcome but writes no handoff document | declined: out of scope for this close - recorded here so the next run does not rediscover it, and the stop reason carries the detail a handoff would have |

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not attributable to this retro - the run spans a compacted session · Duration: 15.3h working (wall-clock, 0 recorded idle gaps) · Critic rejects: 27 REJECT / 11 APPROVE over 38 units, in 5 independent passes
