# RETRO-0091: The close converges and its findings count: the sprint that reviewed itself at the boundary

> **Date:** 2026-08-03
> **Batch:** BG0489, BG0492, BG0499, BG0502, US0616, US0617, US0618, US0619, US0620, US0621, US0622, US0623, US0624
> **Goal:** A close converges in one pass and its findings count - nothing is repaired inside the close, a repaired REJECT has a route back to covered, and no close gate reports a green it did not earn
> **Delivered:** 13 / 13   **Blocked:** 0

## Delivered

39 points, 13 units, both lanes.

**Lane B - the close gates that reported a green they had not earned.** `BG0489`: the
commit-msg verdict is now proven by EXECUTING the hook, not by grepping it - every previous
guard was a `text.index` over the source, which is why the fail-open survived one repair and
returned in a different position. `BG0492`: the verdict binds to the working TREE rather than
the commit, so it no longer authorises every edit made after the suite ran, and `--check` reads
which suite actually ran. `BG0499`: escalation reads both review ledgers and fires from all
three recording commands. `BG0502`: the bounded `--file-and-close` exit prints its close report.

**Lane A, EP0204 - the close's fixed point.** `US0616`: `close` and `stop` refuse while the
tree carries an uncommitted change to a file one of their own batch units declares, with the
rule stated in the doctrine beside the gate. `US0617`: the ledger tells a close-time repair from
an unaccounted unit, derived from dates already on disk. `US0618`: the deliberate exception, per
unit and reasoned. `US0619`: re-running a finished close over an unchanged tree is a no-op that
says so.

**Lane A, EP0205 - a REJECT that can be answered.** `US0620`-`US0624`: `critic repair` records
the answer beside the verdict, append-only; PARTIAL is derived per finding; filed is told from
fixed; coverage distinguishes approved, repaired and unreviewed; and the preflight states the
counts and names the units nobody reviewed.

## Blocked / deferred

Nothing was blocked. Three findings were filed rather than fixed - see **Known issues carried**.

## What went well

- **Boundary review paid for itself, repeatedly.** Six independent passes over two lanes
  returned five REJECTs and 22 blocking findings. Every one became delivery work in the batch
  that caused it rather than close overhead on work believed finished, which is the whole
  argument for reviewing where the work lands.
- **The reviewers found what the author could not.** A one-character closure marking a REJECT
  COMPLETE; a criterion false through the command it named; a recording lane wholly inert; a
  regression over 75 grandfathered rows. None of these were visible from inside the work, and
  each was reproduced by execution before it was believed.
- **The tooling caught its own author four times.** The scrub-site sweep found a git fixture
  whose environment scrub nothing pinned; the reference ceiling is an exact-match ratchet and
  refused the doc addition until it was declared; the style lane refused a provenance tag in a
  consuming-facing script; and the `__main__`-guard check found appended tests that a direct run
  would have skipped. Each was repaired rather than silenced.
- **The suite-claim lane refused this very close.** The tree had moved since the recorded green,
  so the claim no longer described it - `BG0492`'s own tree binding, shipped hours earlier,
  refusing its author. Re-running was the honest answer and took nine minutes.

## What was hard / what stalled

- **Two mechanisms shipped INERT, and fixtures hid both.** `BG0492`'s tree digest returned empty
  on this repository, because `git add -- ':(exclude)<path>'` fails when the path is also
  gitignored - which is this repo's configuration and no fixture's. `US0619`'s recording lane was
  never called by any test; replacing all three call sites with `pass` changed no result. Both
  were found by driving the real thing, one by the author and one by a reviewer.
- **The repair verb was unusable until it was used.** Recording this sprint's own review findings
  through `critic repair` immediately exposed that the ledger markdown-escapes its text, so no
  human-written closure could ever match its finding. Two rounds of that before it worked.
- **A guard that matched nothing looked exactly like a guard that worked.** `lstrip("./")` strips
  any leading `.` or `/` CHARACTER, so every `.claude/...` path became `claude/...` and the close
  guard matched nothing at all on this repository. It passed its fixtures.

## Lessons

- **A mechanism verified only in fixtures is verified only in fixtures.** Two of this sprint's
  own deliveries were inert on the real repository while every fixture passed, and in both cases
  the fixture differed from production in one detail nobody had thought about - a `.gitignore`
  line, and a test that stamped the value it was meant to observe. Run the new thing against the
  tree it ships into, and assert the OUTPUT is non-empty rather than that two computations agree,
  because two empty answers agree perfectly.
- **A matching rule that is convenient is a gate that is optional.** The repair record's
  closure-to-finding match was bidirectional substring because that was forgiving to write
  against. It made a one-character closure close every finding, which turned the review gate into
  a formality reachable from the command line. Where a rule decides whether a gate opens, it must
  resolve to exactly one answer and refuse ambiguity rather than resolving it in the author's
  favour.
- **Fixing the row an operator does not read is not fixing it.** `US0624` changed a checklist
  resolver while the preflight - the command an operator actually runs - built its coverage line
  through an entirely different path, and the criterion's own verifier called the private
  function rather than the shipped one. A criterion that names a command must be driven through
  that command, or it certifies the wrong thing convincingly.
- **A guard reddening a fixture is evidence about the fixture as often as about the guard.** Seven
  rolling tests went red because they never committed their delivered work - a state no real
  close reaches. The guard was right; the fixtures were unrealistic, and had been for as long as
  they had existed.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro.

- A mechanism verified only in fixtures is verified only in fixtures - run it against the tree
  it ships into, and assert the output is non-empty rather than that two computations agree.
- Where a rule decides whether a gate opens, it must resolve to exactly one answer and refuse
  ambiguity rather than resolving it in the author's favour.
- A criterion that names a command must be driven through THAT command; a verifier calling the
  private function certifies the wrong thing convincingly.
- A guard reddening a fixture is evidence about the fixture as often as about the guard.
- Review at the boundary: six passes returned 22 blocking findings that would otherwise have
  been discovered at the close, on work believed finished.

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
| BG0507 | not-stop-ship | agent - the suite-collapse lane writes its green above the collapse check, which is the same fail-open family this sprint closed twice, but it is pre-existing, byte-identical at the base ref, and reached only when a suite collapses | 2026-08-03 |
| BG0508 | not-stop-ship | agent - the close report's imports sit outside its own advisory guard, so an ImportError escapes after the run is stamped; pre-existing on all three emission sites and reachable only when an import genuinely fails | 2026-08-03 |
| BG0509 | not-stop-ship | agent - day-granularity in the close-time-repair split and an unscoped override map; both under-report rather than over-report, and neither holds a gate | 2026-08-03 |
| BG0457 | not-stop-ship | agent - carried backlog, dated 2026-07-31 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| BG0463 | not-stop-ship | agent - carried backlog, dated 2026-07-31 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| BG0469 | not-stop-ship | agent - carried backlog, dated 2026-07-31 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| BG0485 | not-stop-ship | agent - carried backlog, dated 2026-08-02 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| BG0486 | not-stop-ship | agent - carried backlog, dated 2026-08-02 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| BG0500 | not-stop-ship | agent - carried backlog, dated 2026-08-03 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| BG0501 | not-stop-ship | agent - carried backlog, dated 2026-08-03 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| BG0506 | not-stop-ship | agent - carried backlog, dated 2026-08-03 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| CR0509 | not-stop-ship | agent - carried backlog, dated 2026-07-31 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |
| CR0510 | not-stop-ship | agent - carried backlog, dated 2026-07-31 and so predating this run's opening at 13:09; none was raised by this sprint's work. Ruled as a CLASS on provenance, which is a weaker statement than an individual technical assessment and is recorded as such rather than dressed as one | 2026-08-03 |

The ten rows below are this repository's OPEN backlog at the moment the run opened, not
findings this sprint produced. The checklist asks for a ruling on every finding open
during the run, and refusing to give one would leave them reading as unlooked-at. The
ruling is on provenance - they predate the run - and the retro says so rather than
implying each was individually re-assessed.

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
| BG0489 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0492 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0499 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0502 | 2 | 91,620 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0616 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0617 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0618 | 2 | 91,620 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0619 | 2 | 91,620 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0620 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0621 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0622 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0623 | 2 | 91,620 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0624 | 3 | 137,430 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 13 unit(s) measured; 13 of 13 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0489, BG0492, BG0499, BG0502, US0616, US0617, US0618, US0619, US0620, US0621, US0622, US0623, US0624. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- {{what the ratio implies - which units the estimate missed, and why}}

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot.

| Finding | Disposition |
| --- | --- |
| A one-character closure marked a REJECT COMPLETE, a review bypass through the shipped CLI | fixed-in: 46cdf08b |
| US0624 was false through the command it named, and its verifier called a private resolver | fixed-in: 46cdf08b |
| US0619's recording lane was wholly inert - three call sites replaced with `pass` changed no test | fixed-in: 46cdf08b |
| A pre-gate-grandfathered APPROVE read as rejected - two authorities for one question | fixed-in: 46cdf08b |
| BG0492's tree digest was inert on this repository while all six fixtures passed | fixed-in: e53d8076 |
| Porcelain rename parsing, untracked-directory collapse, and raw Affects comparison in the close guard | fixed-in: 46cdf08b |
| The suite-collapse lane writes its green above the collapse check | BG0507 |
| The close report's imports sit outside its own advisory try | BG0508 |
| Day-granularity in the close-time-repair split, and an override that never expires | BG0509 |
| Seven rolling fixtures never committed their delivered work | fixed-in: 46cdf08b |
| The commit-msg suite-claim lane matches a QUOTATION of the phrase it guards, refusing a message that merely describes the rule | declined: the same no-quoting-exception rule the style lane applies deliberately; rewording the message costs seconds and an exception would be the hole |

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
