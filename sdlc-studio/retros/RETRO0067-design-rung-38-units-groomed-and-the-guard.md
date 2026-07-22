# RETRO-0067: Design rung: 38 units groomed, and the guard that took four rounds to stop restating itself

> **Date:** 2026-07-22
> **Batch:** US0311, US0312, US0313, US0314, US0315, US0316, US0317, US0318, US0319, US0320, US0321, US0322, US0323, US0324, US0325, US0326, US0327, US0328, US0329, US0330, US0331, US0332, US0333, US0334, US0335, US0336, US0337, US0338, US0339, US0340, US0341, US0342, BG0256, BG0257, BG0258, BG0259, BG0260, BG0261, BG0264, BG0265 (40 units, 111 points)
> **Goal:** Every story's acceptance criteria would fail if the behaviour were absent, every bug states what makes its fix complete and tested, and any declared dependency records a logical constraint the file census cannot already derive.
> **Delivered:** 40 / 40   **Blocked:** 0

## Delivered

- **US0311-US0342 (32 stories)** - acceptance criteria authored from `{{placeholder}}` scaffolds.
  94 criteria, 91 executable and node-addressed, 3 manual and honestly so.
- **BG0256-BG0261, BG0265 (7 bugs)** - each states what makes its fix complete and tested,
  with the failing node named.
- **BG0264** - the only code this rung shipped: `verify_ac lint` refuses a verifier that only
  reads prose. Four versions, three review rounds.
- **Five dependency edges** - BG0260 on US0315, US0324 on US0323, US0335 on US0332, US0322 on
  US0320, US0337 on BG0257. Two waves where the plan previously asserted all 38 were parallel.

## Blocked / deferred

- Nothing blocked. Round 3's repair is UNREVIEWED: `review.max_rounds` is 3 and the ceiling
  was spent, so no independent pass has attacked the final change to `_runner_files`.
- **BG0266** filed rather than fixed: `file <directory>` is an always-passing prose verifier
  that the guard does not see. Found by round 3, out of scope for a design rung.

## What went well

- **The red-now ledger did what the goal's wording could not.** Two seats independently said a
  counterfactual bar ("would fail if the behaviour were absent") is a belief, not a check.
  Running every verifier at a rung where the behaviour is absent turns it into evidence:
  pass=0, fail=91, manual=3. Nothing vacuously green.
- **The repair-plan gate paid for itself before it exists.** EP0106 is unbuilt, but its
  discipline was dogfooded on round 1: the plan was written, attacked, and REFUTED. The
  proposed fix closed none of the three escapes, and the attacker found two the review had
  missed. That is three rounds saved by one paragraph.
- **The plan review rejected the goal before any work started**, on three specific defects -
  a false claim about six bugs, an information-free clause, and a bar satisfiable by 32
  trivially-true verifiers.
- **Parallel lanes found things nobody asked for**: the silently-dropped second `Verify:`
  line reaching four Done stories, CR0400's stale premise, and BG0259's defect surviving its
  own repair, proven by a hand-run mutant rather than argued.

## What was hard / what stalled

- **One guard, four versions, three rejections, and the same class every time: a RESTATEMENT.**
  v1 judged the target tokens as written. v2 invented a flag-aware split the runner does not
  perform. v3 asserted "grep without `-r` never reads a directory" - true of grep, false of
  this DSL. v4 derived the parse from `_build_command` and left the WALK restated, so `rglob`
  saw hidden and symlinked files `rg` will not read. Each version was defeated by an
  expression the runner reads differently from the way the guard read it.
- **I broke 21 verifiers while trying to make them honest.** Normalising bug `Verify:` lines
  to a prose prefix gave them the head token `red`, which is not a DSL verb, so every one
  became unparseable - and the commit claimed "2/2 passed" in the same breath.
- **Twice I asserted a comfortable conclusion instead of measuring it.** That a surviving
  mutant was equivalent (it was not). That a flag form fails loudly (it exits ZERO and passes
  silently). Both were caught, one by mutation and one because I ran it before writing it down.
- **My directory fixtures were all flat**, so a mutant deleting the walk's non-file filter
  survived while flipping a nested prose tree from refused to allowed. Fixtures that agree
  by construction, unintentionally - the defect a previous sprint shipped deliberately enough
  to record as a lesson.

## Lessons

- **Derive the whole behaviour, not the half you were looking at.** Round 2 derived the parse
  from the runner and left the walk restated; round 3's escape lived in the half left behind.
  A guard that shares one of a tool's two behaviours is still a restatement.
- **A counterfactual bar cannot be checked by any run, so it needs a ledger beside it.** The
  goal asked whether criteria "would fail if the behaviour were absent". At a design rung the
  behaviour IS absent, so running them is free and settles it. Two seats found this
  independently and it should be the standing practice for any design rung.
- **The plan gate belongs before the repair, and the evidence is now in this repo.** Round 1's
  plan was refuted in full. Every previous sprint's rounds 3-10 manufactured the next round's
  defect, and each flaw was in the approach.
- **Check whether the tool you are about to build already exists.** CR0405 asserted CHANGELOG
  had no helper; `changelog.py` had been there all along, and three of its four criteria were
  already met.   <!-- record it: lessons add (project tier). Promote with --global only what generalises beyond this repo -->

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
| US0311 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0312 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0313 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0314 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0315 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0316 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0317 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0318 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0319 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0320 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0321 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0322 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0323 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0324 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0325 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0326 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0327 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0328 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0329 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0330 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0331 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0332 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0333 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0334 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0335 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0336 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0337 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0338 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0339 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0340 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0341 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0342 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0256 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0257 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0258 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0259 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0260 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0261 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0264 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0265 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 40 unit(s) measured; 38 of 40 forecast at plan time.**

**Sprint tokens/point: 834,008** (2,502,024 tokens over 3 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 1.3 points/elapsed-hour** (3 points over 2.299h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: US0311, US0312, US0313, US0314, US0315, US0316, US0317, US0318, US0319, US0320, US0321, US0322, US0323, US0324, US0325, US0326, US0327, US0328, US0329, US0330, US0331, US0332, US0333, US0334, US0335, US0336, US0337, US0338, US0339, US0340, US0341, US0342, BG0256, BG0257, BG0258, BG0259, BG0260, BG0261. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0264, BG0265. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The forecast priced this run as a BUILD: 111 points x the 25,000 seed. It was a DESIGN
  rung that wrote one bug's worth of code, so the seed is being applied to a different
  activity - filed as CR0407 during planning, before the run started, and this run is its
  first out-of-sample data point. The comparison below should be read as evidence about
  CR0407's claim, not as a calibration of the build rate.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it**, or **decline it with a reason**. Both are green. What does not pass is
silence - a finding written down and left to rot.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| A seat verdict of NOT achievable discharges the plan gate identically to yes | BG0262 |
| The goal review keeps no rounds, so rewriting a rejected goal erases the rejection | BG0263 |
| Acting on a plan review invalidates every verdict, including the proposing seat's | CR0408 |
| The seat brief is assembled by the author the review exists to check | CR0409 |
| The state anchor and goal verdict narrated three review rounds where ten happened | BG0261 |
| A false artefact title has no deterministic correction path; `reconcile apply` changed 0 rows | CR0406 |
| A design run is priced at the full build cost of the batch it grooms | CR0407 |
| A second `Verify:` line per AC block is silently dropped, reaching four Done stories | BG0265 |
| `file <directory>` is an always-passing prose verifier the guard does not see | BG0266 |
| `verify_ac lint` cannot reach a bug at all, so "story lint exit 0" says nothing about them | declined: it is the same root cause as BG0256, which is already open in this batch and names the `walk_stories` restriction. A second artefact would split one fix across two units. |
| The velocity write published 834,008 tokens/point for a design rung, from a 3-point denominator | CR0407 (predicted at plan time by its AC3, observed at close; row corrected, rate blanked with the reason) |
| The pre-commit gate is 149s against a 120s budget, +51% since the 2026-07-21 baseline | declined: real but not this run's doing - the suites grew. Belongs to whoever sets the budget, and it is visible on every commit, so it is not being lost. |

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

- Tokens: captured at close from the harness baseline · Duration: one interactive session ·
  **Critic rejects: 3** (rounds 1, 2 and 3, every one finding something real: 4 MAJOR,
  3 MAJOR, 1 MAJOR + 3 MINOR). Round 3's repair is unreviewed - the ceiling is spent.

## Handoff

- [HO-0021](../handoffs/HO0021-every-story-s-acceptance-criteria-would-fail-if.md) - 38 remaining item(s): 27 copilot-tail, 11 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
