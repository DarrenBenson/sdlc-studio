<!-- close-status:begin -->
> **RUN-01KZQ03V closed goal-reached.** 19 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01M05A5M - a DESIGN rung. 12 ungroomed units groomed to red acceptance
> criteria; `sprint breakdown` reports 0 ungroomed, down from 12. The ten stories reached Ready,
> which is this rung's terminal; the two bugs stay Open with criteria, because their vocabulary
> has no Ready and the rung's product for them is criteria rather than a fix.

## THE EXIT CONDITION, AND WHY IT IS NOT A MARKER

**38 criteria: 0 pass, 38 fail, 0 manual, 0 unspecified.**

Zero passing is the column that matters. A criterion that passes before its behaviour exists is
the vacuous verifier this rung exists to catch, and RETRO0071 found three of those in a
comparable run. The mechanic was measured before a single criterion was written: a `Verify:` line
naming a test that does not yet exist reports FAIL rather than `refused`.

The ledger exists because `story_is_ungroomed` returns false the moment the placeholder token is
deleted - an exit condition a `touch` satisfies is not one. QA rejected the goal on exactly that
ground before the run opened.

## WHAT THE GOAL REVIEW CHANGED, BEFORE ANYTHING WAS PLANNED

Two NARROW verdicts and one REJECT, all five findings answered:

* `sprint plan` REFUSES this batch at the default rung. Only `--goal design` accepts it.
* **SC0005 authorised none of it** - scope query `--bugs Open`, and its 20 named bug ids are all
  terminal now. The charter was amended on the record rather than planned around.
* Six of the original 16 needed nothing: 20 of 57 points already groomed. Transitioned as
  pre-work, with the US0586-0588 dependency edges declared and US0590's `Affects` omission fixed.
* Nothing gated the goal. Hence the ledger.
* Two shared-file clusters: the batch is sequential, not parallel.

## THE FINDING THIS RUN RAISED ABOUT THE TOOL

**BG0582, High.** `sprint plan` reads the rung; the close chain does not. `undelivered_blockers`
carries no reference to it, so a design rung whose every story reached Ready exactly as intended
raised 12 status stops, 12 done-gate stops demanding Done, and 12 sign-off stops. The rung is
offered by the planner and unreachable through the closer. **BG0581** is the same asymmetry in
the brief, which promised Review for a run that correctly ends at Ready.

## WHAT IS CARRIED

* **BG0490, BG0493** - groomed here, still triaged rather than built, per the operator's ruling.
* **The TSD is stale.** The plan reported it at open; nothing in this run refreshed it.
* **The disclosure page and the release notes drifted apart three times this session**, each time
  caught by the guard. A derived page and a hand-written claim kept in step by recollection.
