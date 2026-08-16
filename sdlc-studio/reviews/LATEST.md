<!-- close-status:begin -->
> **RUN-01KZQ03V closed goal-reached.** 19 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01M05A5M - a DESIGN rung. 12 ungroomed units groomed to red acceptance
> criteria; `sprint breakdown` reports 0 ungroomed, down from 12. The ten stories reached Ready,
> which is this rung's terminal; the two bugs stay Open with criteria, because their vocabulary
> has no Ready and the rung's product for them is criteria rather than a fix.

## THE EXIT CONDITION, AND WHY IT IS NOT A MARKER

**40 criteria: 0 pass, 40 fail, 0 manual, 0 unspecified.** Ten stories carry 33, the two bugs 7.

That figure has now been wrong twice - 38 here, 40 elsewhere - so it was re-measured at `ba8ac72e`
by running the ledger per unit and summing the `ac=`/`pass=`/`fail=` fields rather than a total
line. 40 is the measured one. The first re-measure was ALSO wrong: a `grep -oE '[0-9]+ pass'` read
`ac=3 pass=0` as "3 pass" and reported all ten stories green. Parse the field, never the
substring: the same fault as the anchor-uniqueness rule, one layer up.

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

A third lane was found while attempting the close, and it is the one that makes the other two
inescapable. `critic.py signoff` does not merely raise a stop - it REFUSES to write: `sign-off
SKIPPED for US0625: its status is 'Ready', which is neither terminal nor awaiting sign-off`,
then `0 unit(s) written`. So the operator cannot clear the sign-off stop even by hand.

**BG0583, High**, filed during the same close: `verify_ac.py run` exits 0 on two inputs it read
nothing for - `--story <id with no file>`, and `--ids <unmatched>`, which prints a line beginning
`error:` and still exits 0 against its own help. It was found because `--story BG0490` reported
nothing and succeeded, and the two bugs were nearly recorded as unmeasured when their 7 criteria
were in fact all red.

## THIS RUN IS OPEN, AND THAT IS THE HONEST STATE

**RUN-01M05A5M has NOT closed.** The work is complete and committed; the ceremony cannot record
it. `sprint close --file-and-close` refuses too, because its deferrable set is exactly
`goal-verdict`, `retro` and `sign-off`, and all 53 outstanding rows are `status`, `done-gate`,
`checklist` and `gate` - so the bounded exit files nothing here. `boundary` needs a rolling policy
this run does not carry, and `stop` would record a run that reached its goal as abandoned.

The remaining routes were both rejected on the record rather than taken:

* **Forcing a terminal** would write Done against 40 deliberately red criteria - a false record in
  the one file every fresh session reads first.
* **Making the closer rung-aware now** would mean editing the gate that is refusing this very run,
  in the session it is refusing, with no independent review. That is the move this repository's
  doctrine exists to prevent, and BG0582's own fix must be delivered by a session it is not
  unblocking.

So the run stays open and the wall is recorded. The goal verdict (`achieved`), RETRO0103, the
lessons and the mirrored installed copy are all landed; what is missing is the state flip, and it
is missing because the tool cannot honestly perform it.

## WHAT IS CARRIED

* **BG0490, BG0493** - groomed here, still triaged rather than built, per the operator's ruling.
* **The TSD is stale.** The plan reported it at open; nothing in this run refreshed it.
* **The disclosure page and the release notes drifted apart three times this session**, each time
  caught by the guard. A derived page and a hand-written claim kept in step by recollection.
