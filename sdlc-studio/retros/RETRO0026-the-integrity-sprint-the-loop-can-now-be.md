# RETRO-0026: The integrity sprint: the loop can now be falsified, and it falsified the estimator again

> **Date:** 2026-07-14
> **Batch:** BG0133, BG0134, BG0135, CR0252, BG0136
> **Goal:** make the measurement loop honest, and close the P1 spec drift
> **Delivered:** 5 / 5   **Blocked:** 0

## Delivered

- BG0133 - the keystone. The forecast is now RECORDED at plan time, with the constants that produced
  it, and `accuracy` reads that record instead of re-deriving it from the live constants. The
  re-derivation path is deleted, not left as a fallback. An in-sample row is labelled and excluded
  from any figure shown as evidence.
- BG0136 - the filer demands what the planner demands, from ONE shared definition of groomed: it
  hands the body it is about to write to `sprint.breakdown()` rather than restating the rule.
- BG0134 - the engagement-floor check refuses instead of printing a failure and exiting 0.
- BG0135 - an orphan index row is now seen by both reconcile and the link checker.
- CR0252 - the specs describe the product again, with five new ADRs. The only outstanding P1, closed.

## Blocked / deferred

- Nothing blocked. Six new artefacts were RAISED by the work: BG0137, BG0138, BG0139, BG0140,
  CR0261, and RFC0035/RFC0036 from operator questions during the run.

## What went well

- **The gates keep catching their own authors.** CR0260's breakdown gate refused three bugs our own
  filer had written that same day (BG0136). The transition gate refused two bugs to Fixed until a
  verification depth was recorded. The commit gate blocked a duplicate CHANGELOG heading. None of
  this was in any subagent's report.
- **Verifying by ATTACK, not by reading.** BG0133 was proven by doubling both forecast constants in
  memory and checking that no recorded estimate moved. A report saying "it reads the recorded value"
  would have been believed; the attack is what made it true.
- Every subagent stayed in its lane across four concurrent agents on one tree, and each one reported
  the scope it exceeded and why.

## What was hard / what stalled

- **The sprint could not measure itself.** BG0133 built the forecast recorder, so the plan that
  launched BG0133 ran before the recorder existed. All five units would have reported UNFORECAST.
  The plan-time forecast was recoverable only because `--write` had persisted `sprint-plan.json` and
  it was committed - so the record existed, in a different place, by luck rather than by design.
- **Hand-arithmetic was wrong, and the record was right.** The per-unit ratios reported mid-sprint
  were computed by hand and two were wrong (BG0133 was quoted at 73,400; the plan actually forecast
  63,800). Checking the recorded plan beat trusting the arithmetic - which is the whole thesis of
  BG0133, demonstrated accidentally on its own sprint.
- The forecast log BG0133 created lives in gitignored `.local/`, so it does not survive a clone
  (BG0140). The fix that made the estimator falsifiable stored its evidence where a fresh checkout
  cannot read it.

## Lessons

- Verify a fix by ATTACKING it, not by re-reading it. BG0133's proof was to double the constants and
  watch the recorded estimates refuse to move. Every report in this sprint would have passed a
  reading; only the attack established the fix.
- A record kept in a gitignored working directory is not a record. The evidence that makes a loop
  falsifiable must survive a fresh clone, or the loop is only falsifiable on one machine.
- The tool that measures a sprint cannot be built by that sprint. Anything self-measuring needs its
  instrument in place BEFORE the run it is supposed to observe, or its first data point is missing.
- A decoy field beats a correct one: `templates/core/cr.md` carried a placeholder `**Effort:**` above
  the real one, and `extract_field` takes the first match - so every full-template CR was unsized to
  the planner whatever `--effort` said. When a parser takes the first match, a duplicate field name
  anywhere above the real one is a silent override.
- A resolved-but-inapplicable signal is more dangerous than an absent one. The router defaults a
  MISSING signal to 0.5 and lowers confidence, but a markdown file RESOLVES the code-complexity
  signal to zero - so a docs unit scores trivial with HIGH confidence (BG0139).
- Before tuning a coefficient, check that its input correlates with the target at all. The cost
  model was recalibrated TWICE (5,000, then 600) and both refits were noise: the seed correlates
  with actual cost at r = -0.006. A miss tells you the output is wrong; it does not tell you whether
  the fault is the SCALE or the AXIS, and those need opposite fixes. The diagnostic is one line, and
  nobody ran it for two sprints.
- A plausible story fitted to a real pattern is not a finding. This retro originally recorded that
  the estimator was "chasing a standard that moved" - that the briefs got harder and the work grew
  beneath them. It was refuted by data already on disk: tokens PER ACTION are flat across all three
  sprints, so nothing about the cost of the work moved. The story explained every observation and was
  wrong, because nobody asked what number would falsify it.

<!-- amended 2026-07-14, after the close: the operator asked which AXIS was wrong, rather than what
     the estimate was. That question produced the three lessons above and CR0262, and it arrived
     AFTER this retro was gated. Amended in place rather than deferred to RETRO0027, because the
     finding is about THIS sprint's data and would have been mis-attributed to the next one. The
     learning loop assumes findings arrive before the retro closes; this one did not. -->

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Seed | Estimate (plan-time) | Actual | Ratio (est/actual) | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- |
| BG0133 | 23 | 63,800 | 217,139 | 0.29x | 1431s | claude-opus-4-8 |
| BG0134 | 0 | 50,000 | 71,935 | 0.7x | 428s | claude-opus-4-8 |
| BG0135 | 52 | 81,200 | 173,804 | 0.47x | 1246s | claude-opus-4-8 |
| CR0252 | 0 | 80,000 | 205,534 | 0.39x | 1134s | claude-opus-4-8 |
| BG0136 | 39 | 73,400 | 234,091 | 0.31x | 1767s | claude-opus-4-8 |
| **Batch (rated units only)** | | **348,400** | **902,503** | **0.39x** | **6006s** | claude-opus-4-8 |

**5 of 5 unit(s) measured; 5 of 5 forecast at plan time.**

Forecast by `base=50000 tpc=600`, recorded at plan time. IN-SAMPLE: the constants in force were FITTED to these actuals. This ratio is TRAINING ERROR - it lands near 1.0x by construction and is not evidence the estimator works. It is excluded from the accuracy the planner reports.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

**Were the estimates any good? No - and this is the SECOND consecutive out-of-sample falsification.**

Every one of five units under-forecast, again, monotonically. That is **eleven of eleven units across
two independent sprints, all missing in the same direction**. The worst miss is BG0133 itself (0.29x),
and the second worst is BG0136 (0.31x) - the two units that required the most judgement.

CR0252 is the diagnostic case. A docs-only unit has complexity 0, so the model has nothing to read and
falls back to the effort proxy: forecast 80,000, actual 205,534. The predictor cannot see the work
because the work is not in the code.

**A model that misses monotonically, in the same direction, on every unit of two independent sprints is
not mis-tuned. It is measuring the wrong thing.** The constants remain unchanged - re-fitting to 16
points would be the third repetition of the error this project has now documented twice - but the
question for the operator is no longer "what coefficient?" It is:

**Is there a plan-time predictor at all?** Cost tracks work done (tool-uses, r = 0.926), and work done
is unknowable before the work is done. The live alternative is to drop the per-unit estimate entirely
and keep only the batch history: "the last two sprints of five units cost 642k and 902k" is a defensible
basis for planning the next one. A per-unit number that has never once been right is not.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| The forecast log lives in gitignored .local/, so the falsifiability fix does not survive a clone | BG0140 |
| Every archived index row link is wrong-depth: 361 dead links on GitHub | BG0137 |
| The model router scores a docs unit trivial with HIGH confidence; its dominant signal is the falsified predictor | BG0139 |
| TS0001 carries 13 broken relative links, and nothing validates links inside artefact bodies | BG0138 |
| The model that delivered a unit is captured in telemetry but is not on the artefact, not in the committed history, and not in git | CR0261 |
| A sprint report should compose delivered value, accuracy, lessons, tickets raised and models used - and price rework, not counterfactual savings | RFC0035 |
| Running several sprints unattended should regenerate each plan at its boundary, not replay a frozen queue | RFC0036 |
| A story is still created ungroomed by `artifact new` - the filer gate closed the bug/CR path only | declined: not filed as a separate ticket. Stories are minted by decomposition batches rather than filed as findings, so the same demand is the wrong shape there and needs the decomposition path designed first. Recorded here so it is not lost, and it belongs to whoever next touches decomposition. |
| The estimator is falsified a second time (0.39x); the predictor, not the coefficient, is wrong | CR0262 |
| The forecast seed is INERT: max_cognitive correlates with cost at r = -0.006 and with work at r = -0.001, so no coefficient can ever work | CR0262 |
| The learning loop assumes findings arrive BEFORE the retro closes. This sprint's most valuable finding arrived after it was gated, and had nowhere to go | declined: recorded here as an amendment rather than filed. Amending the retro is the right answer when a finding is about that sprint's data, and it worked. A mechanism to force it would be ceremony over a case that is rare and self-correcting - the operator asked, and the loop absorbed it. Revisit if it recurs. |

## Close loop (gated)

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated

## Metrics

- Tokens: 902,503 (5 units, all measured) - Duration: 6,806s of worker time - Critic rejects: 0
