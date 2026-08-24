<!-- close-status:begin -->
> **RUN-01M0CT8P closed goal-reached.** 6 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M0JD1W - a unit's own evidence made honest. Six units, 21 points.
> `revert-check` reports a test that never reached the change; `Verification depth` reads its
> counts from the mutation ledger and seals them.

## THE HEADLINE: THE INSTRUMENT REPORTED AGAINST THE SESSION THAT BUILT IT

Registering the close's newly-executed mutants invalidated 22 earlier registrations - they had
run against `verify_ac.py` and `gate.py` as they stood BEFORE the close's repairs, and
registration is keyed on target content hash. `depth` dropped from `executed 5` to `executed 3`
and NAMED the unsupported rows.

Nothing else would have said a word: suite green, every criterion passing, stale counts sitting
in the fields looking correct. All 22 were re-executed. Every unit now reads `not-run 0`.

## THE COST WAS THE REVIEW, AND THE CAUSE WAS A RULE I BROKE

Delivery: 3 rounds. **Test-plan plan review: 5 rounds**, rejecting three units three times;
every round's blocking findings were closed by the next, and round 5 APPROVED all three.

The dominant cause was hand-editing plan tables that `verify_ac.py testplan derive` OWNS. That
produced a FUSED row inside US0674's AC4 Title cell - readable by a human, invisible to
`testplan_rows_by_criterion` - so that unit's own derived field said "plan rows 8; executed 8;
not-run 0" and every figure was computed over a table missing a row. Running the tool fixed it
and three wrong Title cells in one command.

What the rounds found that was not mechanical:

- a FALSE KILL: US0671 AC8's declared mutant SURVIVED, because its control asserted only that
  AC1 came back exempt - which a mutant exempting EVERYTHING satisfies too
- `_first_three`, added to repair a SILENT TRUNCATION finding, shipped with no test and no row
- twice, a test that MOCKED OUT the mechanism its own criterion was about: `_base_blob` patched
  wholesale, and `_first_three` tested in isolation while the criterion was about the lane
- two superseded `killed` rows left live in the ledger, correct only by registration order
Three of the five delivery-round findings were recurrences of recorded lessons: **LL0040**
(a library test is not a lane test), **LL0013** (an enumerated list exempts what it forgot),
**LL0044/LL0045**. Read, and not applied. The fix is not more review - it is mechanising those
classes, and **CR0554** and **CR0539** would do it.

## NUMBERS

Delivery ran at **128,183 tokens per point against 525,434 on the previous run**, with the
forecast inside 1% for the first time. The close then cost more than the delivery.

Appetite read 4,308 minutes of 2,880 - it measures CALENDAR AGE (CR0551), so a run left open
overnight burns it without work. Reset to 5,760 as a recorded standing decision, interim until
CR0551 lands.

## THE NEXT RUN IS DECIDED, AND IT IS NOT THE BUGS

`review.test_plan_after: "2026-08-01"`. **20 of 21 open bugs are past that cutoff and exactly
one has a test plan.** Each therefore needs a plan authored AND independently APPROVED before
it can reach Fixed - the gate that cost this run five rounds, with no `--force` past it.

BG0606 is the proof: its fix SHIPPED and was independently approved, and it is still Open
because closing it needs a sixth plan review for work already reviewed.

So **CR0549 and CR0550 come first** - held as US0677-US0683, 24 points. CR0549 because
`route.estimate` scores whole declared FILES, so 87% of 603 bugs tier `full`; CR0550 because
the test-plan gate is date-scoped and cannot be narrowed to the units that earn it. Operator
decision, 2026-08-24.

## OPEN

| Id | What |
| --- | --- |
| BG0605 | the repair ledger computes outstanding findings per RECORD, so two partial repairs both read PARTIAL |
| BG0607 | a unit's verdict is the LAST row written, so an APPROVE after a REJECT makes a rejected unit read approved |
| BG0608 | the budget line leads with the seconds figure BG0594 proved uninformative |
| BG0609 | `transition.py annotate` has no `--fields-file`, so a backticked value is EXECUTED and its output stored |
| CR0552 | `revert-check` mutates the live working tree - the shape that destroyed a reviewer's uncommitted work |
| CR0554 | a row killed by a test no criterion names reads as `killed` |

BG0607 is the one to read next: three of this batch's units carry a seat REJECT that
`critic show` masks behind a later APPROVE. Each is answered by a recorded repair, but the
roll-up cannot say so - so the two-role gate can today be satisfied by recorder ordering.
