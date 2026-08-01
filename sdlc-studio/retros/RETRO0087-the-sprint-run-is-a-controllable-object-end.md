# RETRO-0087: The sprint run is a controllable object end to end: inspectable and mutable in flight, queued as charters, and closed on evidence that can fail

> **Date:** 2026-08-01
> **Batch:** BG0413, BG0415, BG0418, BG0422, BG0423, BG0433, BG0448, BG0460, BG0466, BG0455, US0466, US0470, US0471, US0472, US0473, US0490, US0492, BG0401, BG0406, BG0419, BG0457, BG0459, BG0372, BG0421, BG0463, US0467, US0468, US0469, US0474, US0475, US0480, US0481, US0487, US0488, US0489, US0491, US0482
> **Goal:** The sprint run is a controllable object end to end: inspectable and mutable in flight, queued as charters, and closed on evidence that can fail.
> **Delivered:** 9 / 37   **Blocked:** 28 carried, each with a recorded reason

## Delivered

**9 units, 27 points of a 37-unit 150-point plan.** Nine bugs Fixed across six commits, every
one TDD-red-first, mutation-checked, and landed through a green gate.

The substance is one theme: **a guard that reports green over something it never checked.**

- **BG0413** - a suite that stops running most of itself now BLOCKS the commit. The 0.8 scope
  floor's entire consequence was that a number did not reach a JSON file, so a close that
  deleted eight test classes ran 510 of 5,645 tests and landed green. A separate collapse
  threshold exits 2 and the hook fails the commit; a deliberate bulk removal states itself in an
  ack that is spent on the removal it describes.
- **BG0415** - the budget lane measured 554s against a 380s ceiling while `sprint plan`, pricing
  the same gate, quoted a 317s baseline. One source now, with the drift named, and a plan over
  the ceiling says so. The ceiling was NOT raised to meet the measurement (D0089).
- **BG0418 / BG0459** - `retro validate` always reported an unreplaced scaffold and always
  exited 0 for it; the close kept only the exit code and printed `valid` over a document nobody
  had written. Any leftover is now reported; a retro carrying every shipped demonstration line
  is refused.
- **BG0460** - `DRY_RUN_ACTION_STEPS` restated the chain and had lost `gate`, so that step
  reached the report as neither ok, nor refuse, nor unevaluated. Derived from the chain now.
- **BG0455** - `sprint stop` counted a unit awaiting an independent signature as work the run
  declined to do, pushing the operator to `--force` and overstating what parking threw away.
- **BG0372** - the overhead ratio was declared in the column contract, computed, and dropped at
  the render. It now survives a write/read round trip.
- **BG0466** - a v3 ULID scored 0 against an ordinal cutoff and was exempted as pre-adoption
  legacy, so the provenance check reported clean over the whole id family the product mints by
  default. And the close's placement count never compared the run window at all.
- **BG0422** - the evidence lessons from five consecutive REJECTs are shipped rather than
  observed: LL0050, plus the named-mutant-first rule and the review-before-commit sequencing.

## Blocked / deferred

**28 units, 123 points, carried untouched.** Not attempted rather than attempted and failed:

- **19 stories (84 points)** - the whole feature half. EP0170 (run lifecycle documented),
  EP0171 (in-flight controls), EP0173 (footprint ratchets), EP0174 (duplicate-Verify split) and
  all six of EP0176 (the sprint charter queue). Nothing was started, so nothing is half-built.
- **9 bugs (39 points)** - BG0401, BG0406, BG0419, BG0421, BG0423, BG0433, BG0448, BG0457,
  BG0463.

**BG0448 was deliberately not started, and the reason is the finding.** Its systemic half -
gating `Fixed` on an oracle the way `Done` is gated - rewrites test fixtures repo-wide and is
far beyond its 3 points; the existing depth-gate fixtures all carry unticked criteria and would
have needed rewriting to satisfy it. Its other half is to tick 31 criteria across eight
terminal bugs, which without re-verifying each fix is precisely the unevidenced claim the bug
exists to condemn. Half-delivering it would have produced exactly the artefact it describes.

## The reviews, which are the result

Two independent adversarial seats, fresh contexts in isolated worktrees, 41 mutants between
them. **They rejected seven of the nine units.** Every finding carried an executed
reproduction, and the repairs are worth more than the original delivery.

**The stop-ship: I left the commit gate broken on main for six commits.** BG0413's collapse
signal used exit code 2 - which python itself returns for a missing script file and for an
argparse error - so `test_precommit_window_guard` went red and every commit was refused with a
blank message. My six commits all passed because the gate runs a SELECTED subset, and that test
was never in it. One commit later I shipped the rule "run the full suite before every commit,
never a filtered subset" and did not apply it to the work beside it. The reviewer bisected it.

**A repair that introduced a regression.** Adding `gate` to the derived dry-run step set while
marking it `unevaluated` unconditionally made `clean` unreachable: every `close --dry-run` in
every repo exited 1, and `dry run CLEAN` became dead code. The step's verdict belonged to the
preflight that had already run it - which the original comment said, and which I left in place
directly contradicting the block I added above it.

**Two of my tests survived mutation against the full 5,658-test suite.** One asserted
`status in {"ok", "refuse", "unevaluated"}` - the set of every possible status. The other
asserted a step count by substring, and was satisfied by the digits "10" appearing in an
unrelated retro message from a sibling unit in the same commit. Both were written in the sprint
that shipped LL0050, whose rule is to name the mutant before writing the test.

**Two acceptance criteria were verified by tests that could not fail.** BG0372's AC1 asserted a
column name that already existed at the commit its own history calls "Marked Fixed while
delivering nothing" - it passed OVER the defect and was stamped `Verified: yes` on the date of
that false close. US0558's AC4 never imported `sprint`, so no change to the close could redden
it, which is verbatim the defect BG0418 was filed to fix.

**And one recorded evidence line was simply false.** BG0466's commit message claimed four
mutants all killed, including the backfill mirror. That mirror had no test at all, and
restoring its hole survived the whole suite.

**A third review then judged the repairs, and rejected three of them** - all one shape, in the
reviewer's words: *each repair is behaviourally right on the path it was written for, and
silently wrong on the path where its helper is absent, broken, or never ran.*

- The **shell half** of BG0413's exit-code contract had no test. Three hook mutants - read exit
  2 again, drop the non-empty-note belt, stop setting `fail=1` - all survived the full 589-test
  tools suite, one of them committing green while printing `commit BLOCKED`. One end of the
  contract was pinned and the other was free.
- BG0460's repair traded a guaranteed false negative for a **false positive**: `close_preflight`
  has early returns that never call `run_gate`, and "no gate blocker" cannot tell that from a
  clean pass, so the preview stated `ok gate: run by the preflight against the real tree` about
  a gate that had not run.
- BG0455's new signoff block **fell through to `return True`** where every other uncertainty
  path returns False - so a critic that raised dropped the unit from the stop's refusal. That is
  the defect BG0455 was filed to end, reintroduced through its own repair, and the fail-closed
  mutant survived the entire 5,669-test suite. The "shared matcher" was also a third
  byte-identical copy behind a broad `except`; deleting critic's predicate changed nothing.

All three are repaired: the signoff path fails closed and reads critic's now-public
`is_awaiting_signoff`; the preflight reports `gate_ran` and an unreached gate is `unevaluated`,
never `ok`; and `tools/tests/test_precommit_scope_collapse_lane.py` drives the real hook and
kills all three surviving hook mutants.

**Round 4 confirmed all three and APPROVED.** Baselines taken before any mutation and
re-confirmed identically after (5,676 skill / 593 tools, both green), every claimed mutant
killed, the short-circuit trap closed by instrumenting the real path, `clean` reachable again
under the REAL preflight, and the hook mutants killed against the full tools suite and
attributed to the new module specifically. No new damage: `gate_ran` is purely additive across
`close_preflight`'s three callers, and all thirteen repo guards exit 0. Two non-blocking
findings were raised and filed into CR0511 - a coverage gap on the fourth (RunStateError)
return where `gate_ran` is correct but unpinned, and a pre-existing uncaught `RunStateError`
in `close_dry_run` that `cmd_close` guards before it can be reached.

**Four review rounds to get nine units past the gate.** That ratio is the honest headline of
this sprint, and it is not an argument against the reviews - three of the four found real
defects that the author, the tests and the gate had all missed.

## What went well

**Every unit was mutation-checked before its commit, and mutation earned its cost twice.**
Fifteen mutants were applied across the nine units and two SURVIVED on the first attempt - both
in tests I had just written and believed:

- BG0413's reasonless-ack guard was unreachable, because the caller's truthiness test already
  rejected an empty reason. Deleting the explicit guard changed nothing and no test could tell.
- BG0466's run-scoping predicate could be replaced with a constant: every fixture was either
  unstamped or claimed by a span, so nothing separated "raised outside a batch" from "raised at
  all" - which is AC3 of that bug, verbatim.

**Verifying the premise before building caught five false starts.** All five
`already-delivered` advisories on the batch were false positives of the title-similarity
heuristic, established by reading the shipped code rather than the titles - and BG0415's premise
turned out to be worse than filed (554s, not the 457s recorded).

**The gate did its job on the author.** It refused the first commit twice: an internal
provenance tag leaking into a consuming-facing script, and MD028 in artefacts I had just
edited. The budget guard then refused a documentation draft at 768 lines against a 741 ceiling,
and the content moved to the file the criterion actually names rather than the ceiling moving.

## What was hard / what stalled

**The plan was 1.4x the measured velocity and the run delivered 18% of it.** This was flagged
at plan time - the record showed 107, 112 and 107 points on recent full sprints against a
150-point plan, and the previous sprint delivered 57 of a planned 150 - and the flag was
correct. The estimate was not the problem; the appetite was.

**Repairs break their neighbours, twice, in one sprint.** BG0413's collapse threshold reddened
a pre-existing test that used a 10-against-3400 count, which is now graded a collapse rather
than a drift. BG0372's new columns shifted every cell in three fixtures that paired the live
header with hand-written rows of a fixed width. Both were real signal, and the second produced
the better repair: those fixtures now derive their width from the header they are read against.

**The batch's first commit bundled the pre-condition work with two unrelated bugs.** The
engagement floor advised on twelve artefacts whose ids the message never named. It was
advisory, so it landed - but the attribution is genuinely worse for it.

## Lessons

- **A plan flagged as over-appetite at plan time is over-appetite.** The velocity record said
  107-112 points and the previous sprint delivered 57 of 150. Planning 150 again produced 27.
  A forecast that is questioned and then not acted on is a forecast that was not used.
- **A guard whose only consequence is a missing record is not a guard.** BG0413's scope floor
  computed the right verdict for a 91% test loss and spent it on declining to write a timing.
  Ask what a verdict COSTS, not whether it is correct.
- **Two components that measure the same thing will disagree, and both will look green.**
  BG0415: the budget lane and the planner differed by 44% about one gate, each correct within
  itself. One source, or they drift.
- **A test asserting against a fixture it built itself proves the reader, not the file.**
  BG0372's criteria passed against a hand-written header while the shipped constant carried
  neither column, and both read `Verified: yes` over the gap. Pin the shipped artefact.
- **An assertion over the set of every possible value holds nothing.**
  `assertIn(status, {"ok", "refuse", "unevaluated"})` cannot fail, and it survived mutation
  against 5,658 tests. If the assertion would pass under every outcome the code can produce, it
  is documentation with an `assert` in front of it.
- **A selected test run cannot tell you the tree is green.** Six commits passed a gate that
  never ran the test my first commit broke. The rule against this shipped in the same sprint,
  one commit later, and I did not apply it to the work beside it. Run the full suite before the
  commit, or do not claim the suite is green.
- **Check the criterion's verifier can FAIL before ticking it.** Two criteria here were
  `Verified: yes` over tests that passed at the commit the defect was still present. A green
  verifier proves the verifier ran, not that the work landed.
- **Stopping is a delivery decision, and it is cheaper than half-building.** BG0448 was left
  untouched rather than part-built, because its half-delivered form is the exact artefact it
  was filed to describe.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro.

- Name the mutant before writing the test - if it cannot be named, there is nothing to test yet
  ([LL0050](../../.claude/skills/sdlc-studio/lessons/_index.md))
- Verify the premise before building on it - five of five advisories here were false
- A repair breaks its neighbours; budget for the fixtures it moves
- Plan to the measured velocity, not to the appetite
- A guard's worth is what its verdict costs, not whether the verdict is right

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
| BG0401 | deferred | Darren Benson | 2026-08-01 |
| BG0406 | deferred | Darren Benson | 2026-08-01 |
| BG0419 | deferred | Darren Benson | 2026-08-01 |
| BG0421 | deferred | Darren Benson | 2026-08-01 |
| BG0423 | deferred | Darren Benson | 2026-08-01 |
| BG0433 | deferred | Darren Benson | 2026-08-01 |
| BG0448 | deferred | Darren Benson | 2026-08-01 |
| BG0457 | deferred | Darren Benson | 2026-08-01 |
| BG0463 | deferred | Darren Benson | 2026-08-01 |
| BG0467 | not-stop-ship | Darren Benson | 2026-08-01 |
| BG0468 | not-stop-ship | Darren Benson | 2026-08-01 |
| BG0469 | deferred | Darren Benson | 2026-08-01 |
| BG0415 | accepted-risk | Darren Benson | 2026-08-01 |
| BG0462 | deferred | Darren Benson | 2026-08-01 |
| CR0509 | not-stop-ship | Darren Benson | 2026-08-01 |
| CR0510 | not-stop-ship | Darren Benson | 2026-08-01 |

**On the three rulings added at close.** CR0509 - a review worktree opening at a stale base -
was corroborated four times over by this run: every one of the four independent reviewers began
7 to 9 commits behind and had to fast-forward before the units under review even existed in
their tree. Two of them said so unprompted in their first paragraph. It is not stop-ship because
each reviewer detected it and recovered, but it cost real tokens four times and it is the single
cheapest fix available to the review loop. CR0510 - ceremony proportional to blast radius - is
likewise not stop-ship and is directly evidenced here: a documentation-only unit paid the same
~350s gate as a change to the commit hook. BG0462 is deferred: it is a real guard weakness on
the version-discovery test, unrelated to anything this batch touched.

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
| BG0413 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0415 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0418 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0422 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0423 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0433 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0448 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0460 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0466 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0455 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0466 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0470 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0471 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0472 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0473 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0490 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0492 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0401 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0406 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0419 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0457 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0459 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0372 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0421 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0463 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0467 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0468 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0469 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0474 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0475 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0480 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0481 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0487 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0488 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0489 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0491 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0482 | 8 | 369,144 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 37 unit(s) measured; 31 of 37 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0413, BG0415, BG0418, BG0422, BG0423, BG0433, BG0448, US0466, US0470, US0471, US0472, US0473, US0490, US0492, BG0401, BG0406, BG0419, BG0372, BG0421, US0467, US0468, US0469, US0474, US0475, US0480, US0481, US0487, US0488, US0489, US0491, US0482. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0460, BG0466, BG0455, BG0457, BG0459, BG0463. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
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
finding written down and left to rot. The three are counted separately at close: a sprint
that repaired eleven findings reads as eleven fixed, not eleven declined.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

All three accepted dispositions are shown below, filled in rather than described - the
vocabulary is exact and a refusal is a poor place to meet it for the first time. Replace
every EXAMPLE row; a row left in place is reported at the close.

| Finding | Disposition |
| --- | --- |
| A unit raised and Fixed inside a run never joins that run's recorded batch, so `close_owed` demands a close that already happened | BG0469 |
| The reasonless-ack guard was unreachable behind the caller's truthiness test - mutation found it, the caller now tests `is not None` | fixed-in: 10b6fd54 |
| BG0372's criteria passed against a hand-written header while the shipped constant carried neither column | fixed-in: a455f9e9 |
| The gate is over its ceiling at 554s against 380s, and bringing it under is a performance project rather than a unit | declined: recorded as D0089 - the breach is carried visibly and stated on every plan, since moving the ceiling to meet the measurement is the pattern CR0510 was filed about |
| Commit edb9fdf0 says `fix(BG0469)` but filed no artefact, so two unrelated pieces of work answer to that id | declined: no tool renumbers an artefact and hand-editing `_index.md` is forbidden here; recorded on BG0469 itself |
| The first commit of the batch bundled the pre-condition grooming with two unrelated bugs, and the engagement floor advised on twelve unnamed ids | declined: advisory and already landed; the attribution is stated here instead |

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

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}

## Handoff

- [HO-0039](../handoffs/HO0039-the-sprint-run-is-a-controllable-object-end.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
