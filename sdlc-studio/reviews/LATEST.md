<!-- close-status:begin -->
> **RUN-01M0CT8P closed goal-reached.** 6 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M0JD1W - the instruments that judge a unit are measured from the
> change rather than asserted about it. Six units, 21 points. `revert-check` reverts a unit's
> declared production files to the run's base ref and REPORTS a test that never reached the
> change; `Verification depth` reads its counts from the mutation ledger and seals them.

## THE HEADLINE: THE INSTRUMENT REPORTED AGAINST THE SESSION THAT BUILT IT

Registering this close's newly-executed mutants invalidated every earlier registration for the
same targets. Registration is keyed on the target's content hash, and the close had edited
`verify_ac.py` and `gate.py`, so 22 rows of evidence stopped joining. `depth` went from
`executed 5` to `executed 3` and NAMED the rows that no longer had support.

Nothing else in the toolchain would have said a word. The suite was green at 6,709. Every
acceptance criterion passed. The old counts sat in the fields looking exactly as they had the
hour before. The only thing that knew was the field this sprint built to be derived rather than
typed, and it knew because it is derived rather than typed.

All 22 were re-executed against the current tree. **33 mutants applied, 33 killed, and every
unit in the batch now reads `not-run 0`.**

## THE REVIEW, AND WHY IT COST WHAT IT DID

Round 1 saw only wave 1. US0674 and US0676 - the two gate lanes, the highest blast radius in
the batch - landed in the second commit and reached an independent reviewer for the first time
at the CLOSE. The test-plan plan review had never been run at all. That is the RETRO0089 cause
repeating: review at the boundary, not at the close.

Round 2 ran three seats over all six units, plus the plan review. **Four of six units REJECTed,
on five blocking findings, every one established by execution rather than by reading:**

- the derived-depth seal judged only the FIRST span in a field, so a second span carrying
  arbitrary false counts passed the BLOCKING lane. The tell was position-dependence - the same
  forged span refused before the sealed one and accepted after it.
- the fixture counts were STILL not pairwise distinct after round 1's repair. `criteria` equalled
  `executed`, and killed, survived, equivalent and not-run were all 1. Three swap mutants
  survived the criterion's own verifier beside a live positive control. The false claim "no two
  are equal" was in the test docstring, the commit message and the first draft of the retro.
- the boundary lane's own call to `_record_revert_yield` was unpinned. Replacing the call site
  with `pass` left all ten lane tests green, including the criterion's own selector.
- the exemption path pattern could not see a production file whose extension was not a
  source-code one. Live, not latent: it was exempting BG0560 AC1 on `docs/existing-users.md`.
- the batch's own previous commit made a true sentence false in the release notes' disclosure
  paragraph - four open High in one paragraph, six in the one below it.

## WHAT THE PLAN REVIEW FOUND, WHICH NOTHING MECHANICAL COULD HAVE

Six plan rows across three units declared mutants their own criterion's verifier cannot die on.
The reviewer found them by reading the ledger's recorded kill node against each criterion's
`Verify:` line - two facts the toolchain already holds and has never compared. **CR0554** is that
comparison. It is the cheapest finding in this run and probably the most valuable: a row that
reads `killed` is the strongest evidence this toolchain produces, and it can be produced by a
test the criterion never named.

The rows were re-filed onto criteria whose tests reach them, and nine criteria were added binding
behaviours that already had a passing test and no criterion at all.

## THE HONEST COST

**128,183 tokens per point against 525,434 on the previous run**, and the forecast landed inside
1% - 2,710,181 against 2,691,843 - for the first time on record. That is the delivery half.

The close then cost more than the delivery did, and three of its five blocking findings were
recurrences of lessons already in the registry: **LL0040** (a library test is not a lane test),
**LL0013** (an enumerated list silently exempts what it forgot), and **LL0044/LL0045** (a shape
list the author chose, and a repair never ruled OVER-CLAIMED). Read, and not applied.

The conclusion is not "review earlier" - that moves where a defect is found, not whether it is
made. It is that these three classes are known and unmechanised, and two of them now have filed
CRs that would catch them for the price of a few lines: CR0554 and CR0539.

## WHAT THIS RUN LEAVES OPEN

| Id | What |
| --- | --- |
| BG0605 | the repair ledger computes outstanding findings per RECORD, so two partial repairs both read PARTIAL forever |
| BG0607 | a unit's verdict is the LAST row written, so one seat's APPROVE after another's REJECT makes a rejected unit read approved |
| BG0608 | the budget line still LEADS with the seconds figure BG0594 proved uninformative |
| CR0552 | `revert-check` mutates the live working tree - the same shape that destroyed a reviewer's uncommitted work (BG0604) |
| CR0553 | the exemption reason floor counts characters, so twelve junk characters buy an exemption |
| CR0554 | a row killed by a test no criterion names reads as `killed` |

BG0607 is the one to read next. Three of this batch's units carry a seat REJECT that
`critic show` masks behind a later APPROVE. Every one of those REJECTs is answered by a recorded
repair, but the roll-up cannot say so, which means the two-role gate can today be satisfied by
the order the recorder happened to be called in.
