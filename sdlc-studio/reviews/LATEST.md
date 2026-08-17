<!-- close-status:begin -->
> **RUN-01M05A5M closed goal-reached.** 12 unit(s) in the batch. This was a `design` rung, not a build - its units end at their own terminal and no Done sign-off is owed.
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

## THE WALL, AND HOW IT CAME DOWN

This run could not close at all. `--file-and-close` filed nothing, because its deferrable set is
exactly `goal-verdict`, `retro` and `sign-off` while all 53 rows were `status`, `done-gate`,
`checklist` and `gate`. `boundary` needs a rolling policy this run does not carry, and `stop`
would have recorded a goal-reached run as abandoned. Forcing a terminal would have written Done
against 40 deliberately red criteria.

It was left OPEN on that reasoning, and **L-0344** records why: repairing the gate that is
refusing your own run, in the session it refuses, is indistinguishable from disabling it. The
operator then instructed the repair, which is the only thing that makes it legitimate - and the
independence lost by authoring it here was bought back the only way left, with three adversarial
rounds.

**Two of the three REJECTED, and both found defects that made this close pass.** Round 1: the
scope was `rung != "done"`, which moved the defect onto the `plan` and `triage` rungs; plus two
mutants surviving all 895 tests. Round 2: **the identical scope error was still in the sibling
`_signoff_preflight`**, dropping a hard done-gate blocker for those rungs with no substitute bar,
and the round-1 renderer repair had no test at all. Round 3 (QA) drove 140 lane readings - 10
fixture shapes across 7 rung spellings, both refs - and found every non-`design` rung
byte-identical to the base. That is what an APPROVE here is worth.

Eight of the fourteen mutants came from the reviewers, not from me. `critic record` escalated the
unit to the operator after the second REJECT, and that escalation stands on the record rather than
being worked around.

**The bar that replaced the wall is weaker than it reads, and that is stated rather than hidden.**
BG0586 and BG0588 together mean a design run whose units were groomed before the window, or left
at `Draft`, still closes clean. A smaller wrong than a rung nothing could close, but a wrong.

## WHAT IS CARRIED

* **BG0490, BG0493** - groomed here, still triaged rather than built, per the operator's ruling.
* **The TSD is stale.** The plan reported it at open; nothing in this run refreshed it.
* **The disclosure page and the release notes drifted apart three times this session**, each time
  caught by the guard. A derived page and a hand-written claim kept in step by recollection.
