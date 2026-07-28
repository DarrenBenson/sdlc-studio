# RETRO-0082: RUN-01KYMJEM - a sprint that tells the truth about itself: seams, clauses, and the instruments turned on their own history

> **Date:** 2026-07-28
> **Batch:** RUN-01KYMJEM - 34 units, 112 points: BG0358, BG0360, BG0361, BG0365, BG0366, BG0379, BG0380, BG0381, BG0362, BG0378, US0536, US0550, US0552, BG0356, US0534, US0535, US0537, US0539, US0540, US0544, US0547, US0548, US0549, US0551, BG0355, US0538, US0541, US0542, US0543, US0545, US0546, BG0382, BG0383, BG0384
> **Goal:** A sprint tells the truth about itself: every seam between two units has an owner before the work starts, the goal is judged clause by clause at plan and at close by a panel the author is not on, and the defects this repo's own review raised are repaired rather than carried.
> **Delivered:** 34 / 34   **Blocked:** 0

## Delivered

All 34 units reached a terminal status: 15 bugs Fixed, 19 stories at Review pending the
two-role sign-off. 112 of 112 points. Eight commits, every one through the full gate.

**The seam work (EP0184: US0538, US0539, US0540)** - the batch's reason for existing. Thirteen
of the seventeen round-one majors in RUN-01KYKVZM were seam defects: four directly contradicting
PAIRS, each passing its own acceptance criteria, because a delivery lane reads ONE unit and
review is the first actor in the loop that reads two. `refine seams` maps the pairs of a batch
that share a declared file and reports the ones nobody owns; a `Preserves:` criterion owns a
seam; the map reaches every lane brief; the close names any seam that shipped unowned.

**The goal machinery (EP0185, EP0186, EP0187: US0541-US0552)** - a goal is recorded as clauses
and judged clause by clause, by a panel that REFUSES the author. An open defect is judged
against those clauses rather than against a severity somebody guessed. The review is a bookend:
asked of the content at plan, asked of the outcome at close, with the shortfall supplied rather
than recalled, and a prediction miss reported where the two disagree. A sprint carries its goal
in its name, with the run id canonical so rewording orphans nothing.

**Fifteen bugs**, eight of them found and filed DURING this sprint by using the tools the sprint
was building.

## What the new instruments measured about runs that had already closed clean

This is the part worth keeping. Each of these was true before tonight and nothing could see it:

- **RUN-01KYKVZM: 52 seams, none owned.** The review found the seam defects by hand at the most
  expensive moment; the map shows why nothing earlier could have.
- **RUN-01KYJZGZ: 24 of 33 units** reached terminal carrying a DECLARED proof obligation nobody
  discharged. Both suites green, gate passed, close ran clean (BG0358).
- **The carried-lessons writer read ZERO lessons** out of the file the lane briefs read five
  from - two constants naming two files, and two parsers over one format (BG0365).
- **109 stale index cells**, including 79 bug rows carrying a severity in the Created column,
  while `reconcile detect` reported `drift_items=0` (BG0380). `status.py` reads the index, so
  every backlog figure quoted today came from a source nothing was checking.

## Blocked / deferred

Nothing blocked. The close is held at the two-role gate: 19 stories carry no adversarial verdict
and no independent sign-off, which is the rule working rather than an obstruction.

## What went well

- **The seam map caught the real pair.** US0529 and US0530 - the actual contradicting units from
  the last sprint - are reported by a fixture reproducing their shape, not by an assertion that
  they would be.
- **Grouping units by shared surface made the batch cheap to reason about.** BG0356 and BG0360
  were a contradicting pair: BG0356 ("the guards must agree") was satisfiable by making
  `verify_ac` SKIP bugs, which would have defeated BG0360 ("run a bug's verifiers"). Both would
  have passed their own criteria. Deciding the direction once, in one shared authority, is what
  the seam work exists to make routine.
- **Bugs found by using the tools.** Eight of the fifteen were filed mid-sprint, each from
  running something rather than reading it.

## What was hard / what stalled

- **The criteria floor at the verb broke about twenty fixtures across five suites.** A 176-file
  sweep was tried, judged too blunt, reverted, and replaced with per-failure patches to the
  shared fixture helpers. The blast radius of a correct rule is still a cost, and it was not
  priced at plan.
- **The gate is the dominant cost of the sprint.** ~370s per commit against a 380s budget, +17%
  over baseline. Eight commits is roughly 50 minutes of gate. BG0383 removed that cost for
  artefact-only commits, but almost every unit here touched `scripts/`.
- **Two bugs were filed on FALSE premises**, both caught by tests written to check the fix.
  BG0383 claimed the verdict-reuse path was broken by the same entry (it is not - `surface_files`
  hashes every tracked file deliberately). BG0384 claimed `file_finding` handled criteria
  correctly; it was worse than the other path, writing the stated-absence note OVER four authored
  criteria. The finding recording the defect was written by the defect.

## Lessons

- **A guard that cannot fail is not evidence, and mutation is how you find out.** Three survivors
  this sprint, two of them tests I had just written: the seam owner-check accepted ANY
  `Preserves:` line because every fixture happened to name the shared file, and the carried-file
  test compared two constants that DERIVE from each other, so it passed whatever they said -
  including the wrong name they both had.
- **Verify the premise before filing, not just before fixing.** Two bug reports were wrong about
  the code they described. Both survived writing, review by their author, and a commit message,
  and were falsified by the first test that ran against them.
- **A contradicting pair is decided ONCE, in one place.** BG0356/BG0360 were satisfiable in
  opposite directions. The fix was a single shared authority both sites read, not two consistent
  implementations.
- **An empty measurement is not a finding.** A Batch line naming no units meant "unreadable", and
  the report said "delivered nothing"; a stale cell meant "nothing checked this", and `detect`
  said "no drift". Both read as answers.

## Carried lessons

1. A mechanism that reaches no caller is inert, however well it is tested
2. An absence is not an answer
3. A repair breaks its neighbours, and a rename is cross-unit coupling
4. An enumerated list silently exempts what it forgot
5. Verify the premise before building on it

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0358 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0360 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0361 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0365 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0366 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0379 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0380 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0381 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0362 | 2 | 98,180 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0378 | 2 | 98,180 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0536 | 2 | 98,180 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0550 | 2 | 98,180 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0552 | 2 | 98,180 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0356 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0534 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0535 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0537 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0539 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0540 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0544 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0547 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0548 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0549 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0551 | 3 | 147,270 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0355 | 5 | 245,450 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0538 | 5 | 245,450 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0541 | 5 | 245,450 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0542 | 5 | 245,450 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0543 | 5 | 245,450 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0545 | 5 | 245,450 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0546 | 5 | 245,450 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0382 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0383 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0384 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 34 unit(s) measured; 31 of 34 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0358, BG0360, BG0361, BG0365, BG0366, BG0379, BG0380, BG0381, BG0362, BG0378, US0536, US0550, US0552, BG0356, US0534, US0535, US0537, US0539, US0540, US0544, US0547, US0548, US0549, US0551, BG0355, US0538, US0541, US0542, US0543, US0545, US0546. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0382, BG0383, BG0384. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

The plan forecast ~5,958,262 tokens = 951,082 fixed + 112 points x 49,090. Recorded at plan
time with the rate that produced it, so this retro judges that number rather than deriving a
new one. Points delivered: 112 of 112.

## Actions raised

- **CR0496** - a project-config decision is invisible to the forward-port check, and a
  grandfathering threshold's restore condition is prose no tool reads.
- **CR0497** - the v5 upgrade grandfathers a project's history without recording what it forgave
  or why; a pre-adoption cohort should be discharged by a visible STUB record, not a baseline file.
- **The gate budget** is at +17% and will fail its own lane soon. Not filed: it wants a decision
  about what the gate is for, not a patch.
- **The first independent goal panel is the NEXT sprint's.** The qa seat called this at plan time
  and it held: a capability cannot be dogfooded by the run that builds it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Written at the close of RUN-01KYMJEM |
