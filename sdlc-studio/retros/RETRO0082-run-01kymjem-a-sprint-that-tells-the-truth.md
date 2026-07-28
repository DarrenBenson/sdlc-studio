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

The set stays at five. One displacement this retro, and the displaced lesson is named with why.

- **A mechanism that reaches no caller is inert, however well it is tested.** KEPT, and it earned
  its place twice tonight: five units the operator's question exposed and seven the review did,
  all with passing tests and nothing able to invoke them. It was printed in every lane brief of
  this sprint, read, and not applied.
- **A test written by the author of a fix asserts the shape of the fix, not the property it was
  for.** NEW, DISPLACING *an enumerated list silently exempts what it forgot*. Three mutation
  survivors tonight and two were tests written hours earlier in this sprint; a third survived
  during the repair itself when one guard shadowed another. The displaced lesson is not wrong -
  it fired twice this sprint, in `_INDEX_OWNED_COLUMNS` and in `_fill_acs` - but it is now
  reliably caught by the tooling, and this one is not caught by anything except mutation.
- **An absence is not an answer.** KEPT: an unreadable Batch line read as nothing delivered, a
  stale index cell read as no drift, a `--` placeholder read as a value, and an empty seat panel
  read as a verdict. Four instances in one batch.
- **A repair breaks its neighbours, and a rename is cross-unit coupling.** KEPT: the criteria
  floor at the verb broke twenty fixtures across five suites, and the hook's fallback regex would
  have silently stopped matching when the staged list gained a status letter.
- **Verify the premise before building on it.** KEPT: two bugs were filed on premises that were
  wrong about the code they described, and both were falsified by the first test run against them.

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

**Sprint tokens/point: 46,365** (5,192,890 tokens over 112 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 13.0 points/elapsed-hour** (112 points over 8.616h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

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

| Finding | Disposition |
| --- | --- |
| Index cell derivation destroyed cross-links in consuming projects (data loss, already mirrored to the installed copy) | fixed-in: this run - three defences, mutation-checked, re-ported and verified against the installed copy |
| `artifact new --type story --summary` hard-refused; a bare-string `acs` exploded per character; batch creation lost all-or-nothing | fixed-in: this run - regressions into paths that worked at 59d7b5b8 |
| Seven mechanisms and two parameters that nothing calls | BG0385 (5 pts) |
| `caller-check --unit` single-valued, so a batch check answers about one unit | BG0386 (2 pts) |
| `judge_defects_against_goal` blind to this repo's High/Medium/Low vocabulary | BG0387 (3 pts) |
| Seam owner check matches by naive substring; `Preserves:` honoured outside a criterion; shared file missed under two accepted path spellings | BG0388, BG0389, BG0390 (7 pts) |
| Lane brief seams scoped to the invocation, so the documented one-unit dispatch never shows one | BG0391 (3 pts) |
| `open_run` destroys the plan-side content review, so a prediction miss can never be reported | BG0392 (3 pts) |
| `goal_panel` returns a verdict nobody gave, and drops one under a mismatched clause key | BG0393 (2 pts) |
| Blocker grouping merges different causes and files a criterion covering one unit of many | BG0394 (3 pts) |
| In-flight warning fires only for a unit re-briefed in the same command | BG0395 (2 pts) |
| `cmd_seams` drops unresolvable ids and re-implements the planner's worklist reader | BG0396 (2 pts) |
| `index_derived_issues` blind to the new field drift, so the gate lane asserting the index is derived is green over it | BG0397 (2 pts) |
| `listing_only_paths` never checks the declared read IS a listing, and applies one module's declaration globally | BG0398 (3 pts) |
| Forward-port check reports `in sync` without naming what it did not compare; a threshold's restore condition is prose no tool reads | CR0496 |
| The v5 upgrade grandfathers a project's history without recording what it forgave or why | CR0497 |
| Gate budget at +26% of its 380s ceiling and now OVER | declined: it wants a decision about what the gate is FOR, not a patch - a unit would encode an answer nobody has chosen. Raised in LATEST.md for the next planning session |
| The first genuinely independent goal panel | declined: not fixable inside a batch. The qa seat said so at plan time and the review agreed - a capability cannot be dogfooded by the run that builds it, so the first independent panel is the next sprint's by construction |

## Handoff

- [HO-0036](../handoffs/HO0036-a-sprint-tells-the-truth-about-itself-every.md) - 19 remaining item(s): 0 copilot-tail, 19 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Written at the close of RUN-01KYMJEM |
