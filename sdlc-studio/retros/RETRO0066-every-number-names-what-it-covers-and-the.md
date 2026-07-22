# RETRO-0066: Every number names what it covers, and the guards reach the code - a 100-point batch that its own review rejected twice

> **Date:** 2026-07-22
> **Batch:** BG0247, BG0248, BG0249, BG0250, BG0251, BG0252, BG0253, BG0254, BG0255, BG0256, US0288, US0289, US0290, US0291, US0292, US0293, US0294, US0295, US0296, US0297, US0298, US0299, US0300, US0301, US0302, US0303, US0304, US0305, US0306, US0307, US0308, US0309, US0310
> **Goal:** Every open bug and every High-priority request built, verified and independently reviewed, so the only thing between this backlog and the v5 release is the operator's signature
> **Delivered:** 33 / 33   **Blocked:** 0

## Delivered

All 33 units built, committed and gate-green (BG0256 was filed mid-run and fixed with the batch). Grouped by what they change:

- **Measurement** - BG0248/US0290 (the rate reads the velocity record and REFUSES across
  models), US0288/US0289/BG0249 (the velocity row is owed at close; 24 rows backfilled with
  blanks, never zeroes), BG0252 (main-thread measured, delegated supplied, the sum a lower
  bound), BG0254 (the forecast declares it prices the BUILD), US0301/US0302/US0309 (the
  mutation gate logs cost against yield).
- **Guards that reach** - US0291/US0292 (collision files derive from Verify lines; a
  contradicted `Affects` reported from ONE predicate shared by planner and validate), BG0250
  (a config key four documents described is now read), BG0251 (the floor sees the violation its
  own commit creates), US0307/US0308/US0310 (a declared rewrite window refuses a commit staging
  what it claims), BG0253 (run ids collision-checked).
- **Onboarding** - US0293/US0294 (migrate seeds a missing AGENTS.md), US0295/US0296 (the
  hygiene check verifies the working model, not just pointers), BG0255 (init no longer ships a
  literal placeholder in the first file a new project reads), US0305/US0306 (a non-shell filing
  path), US0303/US0304 (a `test` audit lens), US0297/US0298 (the seats review the Sprint Goal),
  US0299/US0300 (a sprint stops only when nothing can proceed), BG0256 (a stale verifier).

## Blocked / deferred

- Nothing blocked. The batch's terminal state is bounded, not blocked: `review.two_role_after`
  is 192, so every story here reaches Done only with a reviewer-of-record sign-off the authoring
  session is structurally refused. The stories hold at **Review**. RFC0051 records why an agent
  cannot honestly supply that signature, with four options and a recommendation.

## What went well

- **Seven file-disjoint lanes worked.** Two units that straddled two lanes each were deliberately
  held back and built by the author afterwards. No lane collided with another.
- **The engagement floor caught its own sprint.** The `floor-pending` lane BG0251/US0308 added
  hours earlier BLOCKED the delivery commit, correctly finding five bugs shipping with no
  planning pass. They were given real acceptance criteria rather than a waiver.
- **Two filed premises were corrected rather than implemented.** BG0247 claimed the ordering had
  degraded to priority; it had not, and a reviewer verified the correction against git history
  before it was accepted. CR0388's filed mechanism was wrong and its own CORRECTION section was
  built against instead.
- **The reviews earned their cost several times over.** Three independent instances found
  defects no green suite could reach, including two units shipping in one commit that
  contradicted each other.

## What was hard / what stalled

- **The review rejected twice.** Round 1: 11 MAJOR. Round 2 judged the repair 5 CLOSED, 3
  OVER-CLAIMED, 3 MOVED, and found 6 more. Nothing stalled for want of a decision; the cost was
  entirely in proving the work correct.
- **A repair masks the defect beside it - three times this sprint.** Un-stubbing a gate hid two
  hook mutants. Removing the hook's traversal branch left the end-to-end test green because the
  fixture's gate stub refused the record for its own reason. A surviving mutant is often
  evidence about the harness, not the test.
- **Four of the 22 stories minted carried a wrong or incomplete `Affects`**, one written by the
  author minutes after ruling on that exact defect. The strongest possible evidence for CR0347,
  and it is evidence against careful authors, not careless ones.

## Lessons

- **A library test is not a lane test.** The author fixed the engagement floor's false clean,
  mutation-tested it, and wrote "mutation-proven" into BG0251. The three mutants stopped at the
  library functions and never entered the lane the pre-commit hook actually runs; mutating that
  guard to `if False:` left 3,891 tests green while the lane printed the original defect
  verbatim. Pin the surface a user meets: exit code AND printed text.
- **A repair can mask the defect beside it.** If a mutant survives, test that branch in
  ISOLATION before believing it.
- **An estimator's identity is the parameters it takes, not the values they were measured at.**
  `sample_class` compared constants by value, so shipping a re-measured rate would have
  silently emptied the whole-sprint proving term the moment a sibling fix landed.
- **`grep` cannot verify a claim about meaning.** Four ACs passed on prose asserting the exact
  opposite of their criteria, because `grep` is exempt from the vacuity gate by design.
- **Check what a two-point fit cannot tell you** - see Estimate vs actual.
- **A -k selector matching nothing reports NO TESTS RAN, which is not a pass.** Hit by the
  author directly, and it is also how BG0256's story read `Verified: yes` for two days.

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0247 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0248 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0249 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0250 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0251 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0252 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0253 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0254 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0255 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0256 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0288 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0289 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0290 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0291 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0292 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0293 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0294 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0295 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0296 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0297 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0298 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0299 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0300 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0301 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0302 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0303 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0304 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0305 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0306 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0307 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0308 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0309 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0310 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 33 unit(s) measured; 32 of 33 forecast at plan time.**

**Sprint tokens/point: 236,115** (5,194,538 tokens over 22 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0247, BG0248, BG0249, BG0250, BG0251, BG0252, BG0253, BG0254, BG0255, US0288, US0289, US0290, US0291, US0292, US0293, US0294, US0295, US0296, US0297, US0298, US0299, US0300, US0301, US0302, US0303, US0304, US0305, US0306, US0307, US0308, US0309, US0310. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0256. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

**Forecast:** 2,500,000 tokens (100 points x the 25,000 seed).
**Actual: at least 5,194,538** - main thread 1,090,354 (measured from the session transcript
delta) plus 4,104,184 delegated, summed from the reported totals of 18 subagents. A LOWER BOUND:
the transcript carries no sidechain records (BG0252), and round 3's reviewer is still running
and uncounted.

**Per point: at least 51,945.** The previous sprint measured at least 228,884 per point over 18
points. That is 5.5x the points for 1.26x the tokens, which is not a rate at all - it is a large
fixed cost being amortised.

Fitting the only two measured sprints as `fixed + marginal x points`:

| | value |
| --- | --- |
| marginal | ~13,105 tokens per point |
| fixed | ~3,884,023 tokens per sprint |
| seed model | 25,000 per point, NO fixed term |

The seed is roughly the right ORDER for the marginal term. What the model omits entirely is the
fixed one, and the fixed one dominates by about 300x at these batch sizes. Note the shipped
seed's own basis says "No base term: fitting one does worse than not fitting at all" - true of
the data it was fitted on, which was RUNNER-era per-unit measurement with no sprint ceremony,
no review rounds and no close.

**What this fit is NOT.** Two points, both lower bounds, both from sprints that rejected twice,
and of different shapes (18 units versus 32). Two points always fit a straight line exactly, so
the exact figures carry no confidence. What it does give is a falsifiable prediction: a 40-point
sprint should cost roughly 4.4M, not 1.0M. The next measured sprint tests it. Filed as a finding
rather than applied - recalibrating the shipped constant on N=2 would repeat the mistake
BG0254 was filed about.

**Two point-counts are in play, and they must not be confused.** The velocity row published at
this close reads **22 points at 236,115 tokens per point**, because the ledger counts only
TERMINAL units and the 23 stories hold at Review awaiting sign-off - so only the nine bugs
count. The fit above uses **100 points**, the work actually delivered and paid for. Neither is
wrong; they answer different questions. The row will move to roughly 51,945 per point when the
sign-off lands and the stories reach Done, and any reader comparing this sprint to another must
check which denominator they are holding. That the published row cannot be final until a human
signs is itself worth noticing: the cost is spent, the number is not yet earned.

## Actions raised

| Finding | Filed as |
| --- | --- |
| Cost is dominated by a fixed per-sprint term the forecast has no parameter for | CR0391 |
| An operator cannot delegate reviewer-of-record sign-off to an agent | RFC0051 |
| init ships a literal placeholder in every new project's AGENTS.md | BG0255 |
| A Done story read `Verified: yes` for two days against a test that does not exist | BG0256 |
| Nothing reports that the installed skill copy has drifted from the repo | CR0389 |
| `sprint plan`'s batch-selection error does not show the value each flag takes | CR0390 |
| Ten build-blocking ambiguities across five CRs, ruled before the build | declined: ruled as decisions of record D0052 and D0053, not defects to file |
| The operator's sign-off delegation, and what it costs | declined: recorded as decision D0051; the underlying gap is RFC0051 |
| Four prose-writing scripts still lack a non-shell filing path | CR0392 |
| AC2 of the docs checker has no polarity axis and rests on a blocklist | declined: disclosed in US0310 and in the module's stated bound; widening it untested is how this project manufactures its next MAJOR |
| BG0252's delegated capture is not wired into `sprint close` | declined: stated as unfixed in BG0252's Resolution; the library and CLI exist, only the wiring is owed |
| The message-only case of the engagement floor is not closed | declined: a pre-commit hook is not given the message it gates, and a test holds the limit rather than prose |

## Close loop (gated)

- Review round 1: **REJECT** (three independent instances, 11 MAJOR, 9 MINOR)
- Review round 2: **REJECT** (6 MAJOR, 7 MINOR; 5 of 11 repairs closed, 3 over-claimed, 3 moved)
- Review round 3: run at close, against the round-2 repair
- Sign-off: **OWED, and the operator's.** Not taken by the author. See RFC0051.

## Metrics

- Tokens: **at least 5,194,538** (1,090,354 main thread measured, 4,104,184 delegated supplied;
  a lower bound - sidechain records are absent and round 3 is uncounted)
- Duration: one overnight session
- Critic rejects: **2** (rounds 1 and 2; round 3 pending at the time of writing)
- Tests: 3,927 skill + 312 tool, green. Drift 0. Conformance 0 non-conformant. Floor 0
  violations. ~220 hand-applied mutants; 13 survived first time and every one drove a change.
