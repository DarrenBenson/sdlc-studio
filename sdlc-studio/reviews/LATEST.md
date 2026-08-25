<!-- close-status:begin -->
> **RUN-01M0JD1W closed goal-reached.** 6 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M0WCCG - twelve bugs closed, each carrying evidence executed against
> the tree as it stands rather than a claim about it. **The bar is NOT met: BG0607 is open at
> High**, dropped from the batch, and the run closed `partial`. Its fix shipped in this run and was
> WITHDRAWN when an adversarial pass measured it taking whole-workspace conformance from 608/690 to
> 579/690. The re-scope I then wrote said the fix needed a ledger schema change; a second
> adversarial pass REFUTED that from the ledger's own `Brief` column, and it was right. Read
> `known_issues.py --bar` for the live set, never this line.

## THE HEADLINE: I WAS WRONG ABOUT THE COST FOR THREE DAYS RUNNING

I told the operator that 20 of 21 open bugs owed a test plan AND an independent plan review, and
built two change requests on it. **Not one bug owes an independent review.** For a bug the entry
gate NEVER fires - `Fixed` is not in `_IMPL_TARGETS` - and the terminal `_planned_mutant_gate`
has no verdict check, no APPROVE, no independence test.

TWO functions carry the identical `"has no ## Test Plan"` message, and I attributed the bug
refusal to the wrong one. Measured across all 23 open bugs: 21 owed a test plan, 20 a depth
field, 18 ticked criteria, and ZERO owed a review. The five-round ceremony that made the previous
run expensive is a STORY cost.

**D0151 records the rule this broke** - name the population and quote the gate's current
behaviour for it, from source, before filing. I then broke it again within the hour, which is
the honest measure of what a prose rule is worth.

## WHAT THE PRE-CODE REVIEW BOUGHT

It returned NOT-ACHIEVABLE against a 24-unit batch and re-verified all 24 PREMISES rather than
critiquing the ordering. **Six were false**, including the plan's own stated enabler:

- **BG0599** already fixed in its load-bearing half - one `derive` invocation prints eleven
  fault lines across five criteria. The whole W0 justification was void.
- **BG0602** stated cause absent; **BG0606** stale status; **BG0592** code-complete;
  **BG0604 AC4** contradicted by D0149's own text; **BG0610**'s limb already closed.

Three closed for the cost of reading source. The batch was cut from 24 units and 89 mutants to
13 that could actually close.

## ORDER BY WHAT COMPOUNDS, NOT BY SEVERITY

Four of the thirteen repair instruments the run itself uses. BG0611 first, because this run
appends to the ledger it re-walked 620 times per conformance pass; then BG0609, because this run
annotates depth fields through the one verb that executed backticks; then BG0607 and BG0605,
because this run writes into two roll-ups that were wrong. The critic.py/transition.py units ran
as ONE ATOMIC BLOCK - all edits, then all registrations, then all transitions - which cost
nothing and avoided the invalidation that cost the last close 22 re-executions.

## WHAT BIT, AND IS WORTH CARRYING

**A fixture that cannot reach the branch proves the fail-open path.** Two mutants survived
because BG0586's git check is deliberately silent when git cannot answer and the fixture gave it
nothing to answer with. The mutants were fine; the fixtures were not. When a guard has a
documented fail-open, prove it was ASKED before believing what it reports.

**A criterion about an ARTEFACT cannot be verified by a test over CODE.** All three of BG0606's
first mutants survived for that reason - committed while fixing a bug about exactly that.

**BG0581 fired on this run's own planning brief**, which declared a reachable end state of
`Review` for a batch of bugs. That status does not exist in a bug's vocabulary. The unit filed
about it was in the batch being planned.

## OPEN

Nine Medium bugs, none of them in this batch. The ones to read first:

| Id | What |
| --- | --- |
| CR0556 | a bug gets NO independent judgement of its plan OR its code - the only gate is evidence it reports about itself, and this repository holds 612 bugs against 683 stories |
| CR0554 | a row killed by a test no criterion names still reads `killed` |
| BG0612 | the limbs that survived BG0599 and BG0602 |
| CR0557 | BG0463's twenty findings need individual re-triage against HEAD |

CR0556 is the one to read next. This run closed thirteen bugs on self-reported mutant evidence,
which is exactly the situation that request is filed about - and it was filed deliberately
unacted-on, because acting on it first would have made this sweep more expensive.
