<!-- close-status:begin -->
> **RUN-01M36R3D closed running.** 11 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **The sweep run: the backlog tells the truth.** 38 In-Progress discovery requests and 24 claims
> from a July aggregate, each read against HEAD and each carrying a dated `audit ruling`. Two
> requests FINISHED since August are closed; 26 return to Proposed as never-started; 3 retired.
> BG0718 is Fixed after three plan-review rounds, every finding now dispositioned.
>
> Closing review of record: RETRO0119.

## THE HEADLINE: `IN PROGRESS` MEANT `DECOMPOSED ONCE`

The count said 67 live discovery options. Read against HEAD, most were not. In one cluster of
eleven requests, **not a single commit naming any of them is a `feat` or a `fix`** - every one is
refine, decompose or filing paperwork. Six others in another cluster were decomposed on one day in
August and never touched again. A planner reading `Discovery=67` was reading a batch-refine event
as work in flight, and choosing what to build from a number that could not tell the two apart.

The best outcome of the audit was not a closure count. **CR0547 and CR0548 were already
delivered** - every criterion maps to a Done story, and they had been finished since August, held
open solely because they share an epic whose Draft status blocked the derivation. The request was
done; the link was not. Nothing but reading them against HEAD would have found it.

## WHAT THIS RUN FOUND OUT ABOUT ITSELF

**The guard it built does not guard the state it cleared.** US0848 reports a request that is In
Progress, finished by its children and never judged. Run against the real backlog on the day it
shipped: **zero**, because all 37 stalled requests have an unresolved child. It catches a request
nobody closed; what accumulated here was a request everybody abandoned. The goal says the state
cannot rebuild, and after this sweep it still can. Filed as BG0722 at High rather than claimed.

**Three gates caught defects in this run's own work, and none was repaired to let the run pass.**
A shell-hazard guard found the residue of a mangled edit inside a bug's prose. The verify-ratchet
found four cluster stories sharing one verifier, so a regression in any would fail all four and
none would say which. The derived-only corpus ceiling went red because the run filed twelve
findings - a false positive of an absolute ceiling, filed as BG0732 and cleared by giving the
findings real criteria, which the run's own criterion demanded anyway.

**Four of the run's own verifiers were narrower than the criteria they served**, every one caught
by execution rather than by review: two matched `f['kind']` where the tool emits `lens`, one
demanded a duplicate disappear when its criterion also allowed ruling it distinct, and one counted
five lines where twenty-four individual rulings were required.

## WHAT THE REVIEWS COST, AND WHAT THEY BOUGHT

Eight independent review passes ran against this batch: three delivery, five plan-review. They
returned four REJECTs, and **every one named a defect that was really there**.

The sharpest was the cheapest to state. Four cluster stories' AC2 matched `already delivered`
case-sensitively, while every ruling this run wrote says `ALREADY DELIVERED` - so it matched
nothing, and exit 0 was guaranteed whatever the rulings said. A verifier that passes for a reason
unrelated to its claim, recorded as evidence. That was the **fifth** verifier in this run to do
it: two matched `f['kind']` where the tool emits `lens`, one demanded a duplicate disappear when
its criterion also allowed ruling it distinct, one counted five lines where twenty-four rulings
were required. Each was caught by execution, never by reading.

A second finding was ruled **unfixable and recorded rather than repaired**: AC2's mutant is
`accept a title match as evidence of delivery`, and a title-matched ruling cites a unit id
exactly as a verified one does, so no textual check can separate them. Each story now states what
its verifier proves and what execution established instead. The reviewer judged that split honest
BECAUSE it is disclosed in the artefact rather than implied by a green tick.

A third: US0853's AC2 was recorded PARTIAL, and the reviewer approved the disposition then warned
in the same breath that it only means anything if the gate reads it. It does not - `Verified:` is
prose, only the selector's exit code counts - so an honest self-report of a miss was being
laundered into a green. Checked, confirmed, and filed as BG0733 at High. The criterion's verifier
now tests its own claim and correctly fails.

## THE LAST CRITERION WAS MET RATHER THAN EXCUSED

US0853's AC2 says nothing carries forward as a bullet inside another artefact. Two of its fifteen
survivors sat in CR0592 as exactly that, because the filer routes Low findings into a themed
consolidation CR **by design**. It was recorded PARTIAL, and an independent reviewer approved
that disposition - it claims a fail and hands the reader the artefact to check, which is the
opposite of grading your own homework.

Then the honest answer turned out to be available, and it was taken. BG0734 and BG0735 are minted
through `artifact.py new`, with criteria, `Affects` and size, and removed from the bucket. Neither
of the two dishonest routes was used: filing them at Medium would have inflated two severities to
make a criterion go green, and switching off `low_consolidation` would have been repairing the
mechanism that refuses the run. BG0731 still carries the conflict between that mechanism and
D0217.

The verifier was tightened in the same pass, and for a reason worth stating: it scanned the whole
file for `BG0463`, so the very revision row recording this repair would have failed it. A
verifier that measures prose rather than the thing its criterion is about is the same defect this
run met five other times. It now checks finding bullets only.

## BG0718: THREE REJECTIONS, THREE REAL DEFECTS

Round 1 found a fixture claiming an open run that was not one, and a repair that relocated the
defect rather than removing it. Round 2 found the same defect surviving in the legacy pages the
fallback existed to protect. Round 3 verified all four rows as real and discriminating, then
rejected for what no row covered: nothing pinned the window bound OUTSIDE the digest - recording
it as a figure passes all 208 tests in the module and invalidates every page ever filed - and
nothing pinned that the bound reaches the FILED page rather than the derived dict. Six criteria,
six mutants killed, and it stays OPEN: the operator ruled it is not closed on its author's say-so.

## WHAT WAS FOUND AFTER THE FIRST FILING, BY READING THE PAGE

The report filed, passed `check`, and was still wrong in two figures. Both were found by
reading what the shipped commands produced, not by the suite, which was green throughout.

- **The cost row priced the stamped window, not the run.** `run_token_total` ignored the legacy
  `session_token_baseline` whenever any stamp existed. A run already open when the `open` stamp
  shipped has none and never can, so its opening reading lives in the baseline alone: this run
  published 90,809 tokens - the 44 minutes between its two PREPARE stamps - for 9.6 hours of
  work, with every other clause of the row true. US0844 AC5.
- **Mutation evidence was counted without checking it was still evidence.** The page counted
  every ledger row, including rows the ledger reads as NOT-RUN because the mutant was applied to
  bytes the file no longer holds. A run's own later fixes are what stale a row, so the figure was
  at its most wrong exactly when the page is derived. Judged now at the anchor's site. Measured
  after the fix: 36 of 36 rows live, none stale - the claim was true, and is now checked.

Two further defects came out of the same pass. `report` was a registered artefact type with no
index template, so filing the first report left a `reconcile` drift `apply` cannot clear and the
first close of any project ended in a gate refusing the commit the close had just asked for
(US0836 AC5). And `test_autosprint` still asserted the pre-split contract: it went red when the
close tail stopped ending the run, was invisible to its own module, and reached main because the
tail fix was committed on a selected subset - the full-suite rule, broken again by the run that
ships the machinery for keeping it.

Two declared mutants SURVIVED re-execution and were corrected rather than recorded as kills.
US0835 AC1's named the wrong guard - defaulting a missing source to `derived` cannot produce a
passing build, because the resolution check refuses it in the next clause. A mutant that cannot
fail is not evidence, whichever way it reads.

## WHAT DELIVERY REVIEW FOUND, AND WHY IT MATTERED

Two independent seats rejected six of the nine units in round one, and every rejection was a
defect that 33 passing criteria and 2,036 passing tests could not see:

- `stamp_tokens` reached NO CALLER. The report-time meter reading was never taken, so every run
  would have published its cost as zero. `test_run_state.py` was green throughout, which is the
  point: a library test cannot see a missing lane.
- The DORA window stayed open while the run was open, so every later commit entered the run's
  figures - and because this repository ships the paperwork in the same commit as the code,
  COMMITTING THE REPORT invalidated the report. No operator could have obtained a signable page.
- The CI cache nothing wrote meant every re-derivation was a fresh network call with a different
  answer, behind figures the report claims re-derive.
- `transition requirements` raised an uncaught refusal for every unit of a sealed run's batch, a
  regression in a read-only reporting command.
- Two declared mutants had SURVIVED: one assertion searched a whole page for a unit id the close
  pre-flight also prints, and one narrowed on a sentence no fixture ever put two requirements
  into.

The root cause was one question asked too narrowly. The first repair asked "which figures does
the SEAL move?" and excluded three. The question that decides whether a page can be signed is
"which figures does anything but the delivered work move?" - and that answer also included the
live transcript, the open git window and the live forge.

## WHAT IS OWED

- **BG0706**, ruled not-stop-ship: the per-unit coverage gate charges a unit for the added lines
  of a batch sibling sharing its `Affects` file. Measured here at 432 uncovered lines for
  US0832, almost all of them executed by another unit's tests in the same suite. Recorded as the
  wall it is rather than repaired in the run it refuses.
- **The run is OPEN and no report exists.** PREPARE cannot complete while the coverage gate
  refuses the batch, and the anchor block above previously claimed a filed report and a tool
  stamp it never had - a hand-written claim in the one file every fresh session reads first,
  which is the most expensive kind of false claim this project can carry. Corrected.
- **The panel measured what the record had not.** Running all 33 of the batch's verifiers in one
  coverage session against the batch's added lines - which is what BG0706's proposed run-scope
  fix would do - leaves 284 lines uncovered by ANY verifier in the whole run. So the proposed
  fix does not clear this run, and neither does a per-unit commit split, because those 284 lines
  belong to somebody. Only a recorded waiver ends with a sealed run.
