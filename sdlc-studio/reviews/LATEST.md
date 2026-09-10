<!-- close-status:begin -->
> **RUN-01M1YK70 closed goal-reached.** 6 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> Closing review of record: [RV0027](RV0027-run-01m20rwx-closing-review-sixty-six-seat-verdicts.md).
> **Run of record:** RUN-01M20RWX - every Medium open at the base ref, disposed of. Twenty-two
> units, 72 points, 174 mutants registered killed and none surviving. Goal **achieved**: 18 bugs
> at Fixed with their own verifiers passing, 4 stories at Done, and the three findings this run
> itself filed ruled open with a date and a reason. The push and the v5.1 tag stay the operator's.

## THE HEADLINE: THE REVIEW FOUND ONE SHAPE NINE TIMES

Sixty-three seat verdicts across plan and delivery, forty-four of them REJECT, and almost every
blocking finding was the same defect: **a criterion whose words go further than its fixture.**
AC5 named three grep failures by name and tested none of them, so a selector that was simply a
typo classified as healthy on 126 verifiers. AC8 said it judged a printed remedy by RUNNING it
and read the source instead, which is how four remedies came to tell a reader to run a command
the tool now refuses - one of them printed by the very command that does the refusing. AC7
required its values to round-trip and asserted that the WORD "pipe" survived a writer that
replaced the character with a slash. AC4's control was built on a class the shipped code never
emits. In each case the criterion read as met and measured something narrower than it said.

The sharpest finding was a product seat's census rather than a reading: US0819's probe, which
exists to ask whether a criterion can fail, classified a unit as a finding unless a commit
SUBJECT named it - and a repo-wide run showed every one of its 25 findings was a unit the same
commit had delivered. The test could not see it, because it patched the reader out.

## WHAT LANDED

- **US0819/US0820/US0821** - the falsifiability probe. `testplan probe` runs each criterion
  against the tree and reports a PASS as the finding; `sprint plan` refuses a batch carrying an
  unruled one (three modes, default `report`); a ruling is recorded against the criterion's title
  AND selector, and reported STALE when either moves.
- **US0822** - a ledger row is judged by the site its mutant was applied to. The reviewer found
  the benefit was unreachable: `plan_execution`, the join the terminal gate reads, still keyed on
  the whole file's hash, so the anchors reached the commit lane and stopped. 26 rows across three
  units went from `not-run` to counted the moment that was fixed.
- **Eighteen Mediums**, from `check_versions` extracting a version by structure only, through the
  test-plan gate firing at the terminal transition by whatever route reached it, to the corpus
  lane reporting what rose, what went green and what VANISHED by id.
- **D0186** - the v5.1 bar is the RULING, not the count, superseding D0185's first promise.

## WHAT THE SEATS GOT WRONG

Two blocking findings were REFUTED by execution and recorded as OVER-CLAIMED rather than
repaired: BG0657's dead-stamps count (the shipped lane exits 0 here with identities matching, and
two other seats read the same) and BG0630's `--force` regression (the gate's entry call site has
never carried a force guard either, so making one firing waivable would let the same fact be
waived or refused by which route a caller took). A review is evidence, not an instruction.

Three of my own mutant verdicts were RETRACTED for the same reason in reverse: each was applied
to the wrong site - a spy test instead of the sweep, a fixture whose route could not reach the
branch, an edit that killed on a TypeError rather than on its criterion - and a mutant aimed at
the wrong site is a measurement of nothing whichever way it reads.

## WHAT IS OWED

- The push, and the v5.1 tag. Both the operator's.
- The v5.1 cut itself: 119 changelog fragments fold cleanly now, and 59 of them had to be
  repaired by hand first because nothing checks a fragment's shape until the cut tries it
  (BG0662, ruled open).
- Three Mediums ship disclosed and ruled: BG0659, BG0661, BG0662.
