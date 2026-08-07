# RETRO-0098: The repair-evidence rule the doctrine states is the rule the command performs, and the sprint's own thesis was turned on the sprint

> **Date:** 2026-08-07
> **Batch:** BG0541, US0660, US0661, US0564, US0565, US0566, US0573, US0567
> **Goal:** The repair-mutation evidence rule the shipped doctrine states is the rule the shipped command performs, in a mode the operator chose
> **Delivered:** 8 / 8   **Blocked:** 0

## Delivered

- **BG0541** (8) - `transition.py set` reaches a `mutation_evidence_lane` composing
  `repair_mutation_gate` and `verify_no_surface_claim`. Both had zero non-test callers while
  the doctrine told consuming projects the terminal status was refused without evidence. The
  lane sits OUTSIDE the `review.test_plan_after` condition the repair branch sat in, because a
  lane hung there is inert wherever that unrelated date is unset. The exemption is re-derived
  from git's diff rather than from the paths the record itself declares, and an empty or
  unresolvable base ref refuses rather than granting. `reference-doctrine.md` rule 21 enumerates
  its mechanisms and an AST guard checks each is REACHED from the gate ladder.
- **US0660** (8) - `review.mutation_evidence: report`, the default: a survivor becomes a
  severity-rated bug in the backlog and the transition proceeds. Severity is derived from the
  enclosing structure and names the signal it was read from. The close counts this run's
  survivors by severity, from the filed artefacts.
- **US0661** (8) - a measured run records its per-mutant rows, attributed by `run --unit`, so
  the gate is satisfiable by measurement rather than only by the author's typed claim.
  `register --line` exists and is required. A ledger contradicting itself refuses in every mode.
- **US0564, US0565, US0566, US0573, US0567** (18) - the wave that built the gate, closed. Every
  criterion whose When names a command is re-pointed at a test that drives it, and 20 false
  `Verified: yes` stamps were retracted and re-earned.

## Blocked / deferred

- Nothing was blocked or dropped. Ten findings were filed and deliberately NOT fixed, each
  ruled below rather than absorbed.

## What went well

- **The plan review paid for itself three times over.** Three rounds, 24 findings, 21 closed
  before a line of code existed. Every one of the five blocking findings named a plan whose
  test could not fail on its own mutant - and round two found that two of round one's repairs
  had MOVED their defect rather than closed it, which is far cheaper to learn in a table than
  in a diff.
- **Every blocking review finding was established by execution.** Not one arrived as an
  impression. The reviewers built fixtures, applied mutants and reverted them, and the two
  most serious findings of the sprint - an unresolvable base ref granting a false exemption,
  and a second unit's measured run silently erasing the first unit's evidence - were both
  reproduced end to end before being reported.
- **A proposed repair was implemented and reverted.** Round three asked that a corrected
  mutation verdict supersede the earlier row. Building it reddened the test that pins the
  opposite rule deliberately, and the reason is exact: a genuine correction and an author
  registering their way out of a survivor are byte-identical to the tool. The finding is real
  and is filed with an answer that does not open that door.

## What was hard / what stalled

- **The sprint's own thesis caught the sprint.** 61 mutants had been registered across the
  eight units for edits that were never applied - the ledger held claims, which is the exact
  state this work exists to stop counting as proof. Clearing all 61 and applying them for real
  took under ten minutes and turned up two survivors the paperwork had recorded as kills.
- **Registrations go stale on the next edit, silently.** Eight of this run's own were dropped
  by a later registration after an intervening edit, and the loss was found only by re-running
  `--from-plan` by hand. Nothing said a word.
- **Three review rounds is a lot, and it was the right number.** Each round's findings were
  narrower than the last - blocking, then MOVED repairs, then unpinned repairs - which is what
  convergence looks like. What made it expensive was not the reviewing but that two rounds were
  needed to notice a repair had relocated its defect one construct over.
- **The escalation says a unit is not converging when it has just converged.** Every APPROVE
  in this run printed a non-convergence notice, because the count is a lifetime one and the
  notice never re-reads the latest verdict.

## Lessons

- **A registered mutant is a claim; clear the ledger and apply them before believing the
  count.** 61 registrations, 47 applied for real, two survivors the paperwork called kills.
  Register AFTER the last edit to a file, and only from a script that applies, runs, restores
  and registers on a genuine red. (LL0053)
- **A repair relocates its defect one construct over, and the second construct is the one
  nobody checks.** The terminality rule learned If, Try, With and `while True` in round one,
  and was still wrong about `for`/`else`, `match`, `async with`, an inner loop's `break`, and
  a `break` that jumps past the `else`. Five rounds of one rule. Widening a rule is not the
  same as making it right, and the test for the difference is a fixture on the OTHER side -
  bodies that genuinely DO have the property, or the rule can be widened until it claims
  everything.
- **A criterion whose premise is not decidable from what is stored gets satisfied by a
  fixture.** US0661 AC4 demanded that a registered claim be caught disagreeing with a
  measurement. A registered mutant is the author's prose and a measured one is the generator's
  fault class; the two join on nothing. The criterion was narrowed to what the ledger can
  decide and the rest filed - because the alternative was a check that refuses on a comparison
  nobody can make.
- **A fixed line number in a fixture family probes past the end of the short ones.** Every
  severity fixture shared a probe line, and the short one returned `module level` - a different
  wrong answer wearing the same green tick. The line travels with the body now.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A registered mutant is a claim. Clear the ledger and apply them before believing the count.
- A repair relocates its defect one construct over, and that construct is the one nobody checks.
- A criterion whose premise is not decidable from what is stored gets satisfied by a fixture.
- A declaration can only SHRINK a derived surface, so deriving from one is a fail-open.
- A mechanism that reaches no caller is inert, however well it is tested.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

**Two sets, ruled on different grounds.** The ten this run filed are ruled individually
above - two `accepted-risk` (BG0551 and BG0553, both of which limit something this
increment claims, and both named in the shipped doctrine or the artefact that claims it)
and eight `deferred`.

The thirty-five below are carried backlog whose window overlaps this run rather than
findings this sprint chose to leave. Each was read before being ruled, not swept: the open
bugs are `not-stop-ship` because the increment this close signs off is the mutation-evidence
lane, and not one of them says that lane is wrong - they are defects in the planner, the
warning ratchet, the coverage readers, the census and the guards, each with its own
reproduction and none of them made worse by this diff. The open CRs are `deferred` because a
request is not a defect: CR0535 and CR0538 are In Progress and CR0538 is already decomposed
into EP0211 and eight stories awaiting a sprint.

Two of the `not-stop-ship` bugs deserve naming here rather than being read off a table.
BG0535 records 106 red executable criteria across stories already marked Done, and BG0528
records that a delivered unit left at Ready is invisible to every close gate. Both are
tree-wide truths about how this project closes work, both predate this run, and both are
larger than any one sprint - which is the argument for a sprint of their own, not for
holding this one.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0545 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0546 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0547 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0548 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0549 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0550 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0551 | accepted-risk | sdlc-studio panel | 2026-08-07 |
| BG0552 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0553 | accepted-risk | sdlc-studio panel | 2026-08-07 |
| BG0554 | deferred | sdlc-studio panel | 2026-08-07 |
| BG0457 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0463 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0469 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0486 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0508 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0509 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0512 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0519 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0522 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0523 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0526 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0528 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0529 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0531 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0532 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0534 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0535 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0536 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0537 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0538 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0539 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0540 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0542 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0543 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| BG0544 | not-stop-ship | sdlc-studio panel | 2026-08-07 |
| CR0509 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0528 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0529 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0530 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0531 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0533 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0534 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0535 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0536 | deferred | sdlc-studio panel | 2026-08-07 |
| CR0538 | deferred | sdlc-studio panel | 2026-08-07 |

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
| BG0541 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0660 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0661 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0564 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0565 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0566 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0573 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0567 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 8 unit(s) measured; 8 of 8 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 9 pass(es) over 3 unit(s), 6 rejected

  code review: 15 pass(es) over 8 unit(s), 6 rejected

  ratio: 1.67 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0541, US0660, US0661, US0564, US0565, US0566, US0573, US0567. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The plan-time forecast was recorded against 33 points. Three review rounds re-priced the
  three new units from 5 to 8 each and the batch finished at 42, so the recorded number is 21%
  under what was delivered - and the retro judges the recorded one, which is the point of
  recording it. The growth was not scope: every added criterion came from a review finding
  about a test that could not fail. That is the cost of writing a plan whose rows are lethal,
  and it is paid at plan time or at review time, never nowhere.

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
| `testplan derive` refuses a sound plan while the module's own helper finds no fault | BG0545 |
| The origin-tag guard demands a diff attribution from a plan review that has no diff | BG0546 |
| The gate ladder assigned its warning variable where its docstring says accumulate | BG0547 |
| The AC parser silently drops a criterion headed `AC2a` - the count is the only symptom | BG0548 |
| A converging APPROVE still prints the non-convergence escalation | BG0549 |
| `register` drops a file's earlier registered mutants without saying so | BG0550 |
| `repair_mutation_gate` derives its surface from the artefact's own `Affects` | BG0551 |
| A registered mutant cannot be joined to a measured one | BG0552 |
| A mistyped mutation verdict cannot be corrected, and now hard-refuses | BG0553 |
| Severity under-rates the explicit `return None` idiom, this codebase's own | BG0554 |
| The mutation-evidence lane had no caller while the doctrine said it refused | fixed-in: bf88cae5 |
| An unresolvable base ref granted a false no-mutatable-surface exemption | fixed-in: b7a2d1c4 |
| A second unit's measured run erased the first unit's evidence, silently | fixed-in: b7a2d1c4 |
| The contradiction check turned the default mode into an unstoppable block | fixed-in: b7a2d1c4 |
| The close counted every survivor ever filed while claiming to count this run's | fixed-in: b7a2d1c4 |
| The severity signal stated things false of the body it read | fixed-in: ad7a69e7 |
| The test-noise ratchet was RED on main and enforcing nothing | fixed-in: bf88cae5 |
| Superseding a corrected registration would open the escape the worst-verdict rule shuts | declined: the correction is real, but the fix asked for opens a door somebody deliberately shut - BG0553 carries the recorded-retraction answer instead |

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

- Tokens: captured by the close from the harness · Duration: one session · Critic rejects: 10 (3 plan-review, 7 delivery), all converged

## Handoff

- [HO-0055](../handoffs/HO0055-the-repair-mutation-evidence-rule-the-shipped-doctrine.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
