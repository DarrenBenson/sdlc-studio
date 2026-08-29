<!-- close-status:begin -->
> **RUN-01M0YXN3 closed goal-reached.** 4 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M11MEP - the ceremony's own record made to answer, or to say it cannot.
> Ten units, 58 criteria, 76 mutants all killed. Goal judged **PARTIAL** on measurement, not on
> impression. Release bar MET, measured after every unit reached terminal.

## THE HEADLINE: A REPAIR THAT MOVED THREE TIMES, AND TESTS THAT PINNED NOTHING

Seven delivery REJECTs across five of ten units. Not one was cosmetic.

**BG0623 was rejected three times and the defect MOVED every time.** Round 1 assumed the H1 was
line 1, so a document with no heading lost its `Status` line at exit 0. Round 2 took the first
line whose `lstrip` starts with a hash - which destroyed a fenced comment, a `#hashtag` and an
indented code line. Round 3 required a real ATX heading and tracked fences, and still overwrote
`## Summary` whenever no H1 existed, and still destroyed a hash inside a four-backtick fence, an
HTML comment and YAML front matter. Each repair fixed the shapes its criterion named and broke
the next shape along.

What ended it was not a longer list of shapes. The licence to OVERWRITE is now narrow: only an
unambiguous level-one ATX heading, outside every container that suspends markdown, is ever
replaced. Everything else - including a `##` in a document with no H1 - gets an INSERT. A shape
the finder does not understand costs a duplicate heading a human can see, never a deleted line.
**When a defect survives two repairs, stop enumerating cases and make the dangerous operation
harder to reach.**

**A positive control asserting an error string is ABSENT pins nothing.** Both BG0624 severity
suites passed against a guard mutated to refuse EVERY severity, because they asserted only that
`is not one of` did not appear - equally true of a command failing for an unrelated reason.
Strengthening them to assert success then exposed a second vacuous case: the fixture had never
supplied `--points`, so the creator had been refusing on its grooming gate the whole time.

**A regression that wrote before it refused.** BG0619 widened `find_by_id` to reach retros, which
made resolving and being LINKABLE diverge: `file --parent RETRO0109` passed the pre-mint guard,
wrote the child, indexed it and stamped a one-way Parent link, then exited 1 printing "file
refused". The base ref refused before writing anything.

**Reviewers ran mutants the author had not named, and thirteen survived.** Four on BG0623's
heading finder - one of which *repaired* three live data-loss paths and was invisible to the
suite, which is the clearest possible sign the tests pin the wrong thing. All thirteen are killed.

## WHAT TO READ BEFORE THE NEXT RUN

**LL0053 cost this close seventeen re-executions.** Mutant registrations are keyed on target
content, so every later edit to a shared file evicts them. BG0622 and BG0626 were BLOCKED at the
close; BG0613, BG0617, BG0625 and BG0629 read STALE. Register after the LAST edit, then re-run
every unit's transition dry-run - and expect to do it again if the close itself edits a target.

**Two of my own mutants survived for the wrong reason.** A phase-specific relocation cannot reach
a delivery fixture, and a partial `cmd_show` edit leaves the json branch intact. A mutant that
survives because it was mis-specified is not evidence of coverage; check the mutant before
believing the survival.

**The goal was judged PARTIAL, and both misses are countable.** Clause 1 wanted eleven units;
nine of the original eleven landed (BG0591 and BG0614 dropped with recorded reasons, BG0629
added). Clause 3 wanted zero non-conformant; the base ref carried 2 and this tree carries 7 -
US0569-US0576, none of them in this batch. They are non-conformant BECAUSE the batch worked:
BG0625 and BG0629 repaired the verdict roll-up, which stopped masking their unanswered
rejections. **Clearing those seven is the next run's first question.**

## OPEN

Eight findings filed and carried, all ruled not-stop-ship: **BG0633** (a THIRD Severity writer -
`transition.py annotate` takes `major` at exit 0, found by falsifying this batch's own "nothing
else writes it" claim), **BG0634** (the repair ledger truncates a finding label mid-code-span,
leaving an unbalanced backtick that blocked this very commit twice), **CR0562** (nothing ticks a
delivered unit's criteria, so a compulsory close row can only be answered by hand - 58 boxes this
close), plus BG0627, BG0628, BG0630, BG0631, BG0632.

Sign-off is RECORDED for all ten units. Nothing is owed on this run.
