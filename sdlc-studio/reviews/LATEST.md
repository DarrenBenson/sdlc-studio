
<!-- close-status:begin -->
> **RUN-01M2SPNS closed running.** 9 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M2SPNS is OPEN and a report is filed.** 9 unit(s) delivered, none terminal - under
> D0213 no unit is terminal until the SEAL, so each has cleared its terminal gate rather than
> reached Done. PREPARE completed once the coverage lane stood down under D0214, and RPT0001 is
> the page to be signed. What remains is the operator's single act:
> `sprint sign --report RPT0001 --principal "Darren Benson"`. The run's state is the run record,
> not this file.
>
> Closing review of record: RETRO0118 (`sdlc-studio/retros/RETRO0118-run-01m2spns-the-close-splits-and-the-run.md`).
> **Run of record:** RUN-01M2SPNS - a run ends with one page it can be judged on, and one act
> that signs it. Nine units: the close split into PREPARE and SEAL, the three holds a report is
> refused over, and the six units that compose the page itself.

## THE HEADLINE: THE SIGNATURE IS NOW THE LAST THING THAT HAPPENS

RUN-01M2JA6J paid for this batch. Its operator's approval was applied and then roughly two hours
of CI, reviews, repairs, cascades and paperwork followed it, because `--apply-signoff` ran the
fan-out AND the close tail. `sprint close` is now PREPARE: every step that can change a fact -
the ten-step chain, the handoff, the velocity row, the reconcile - then it files the report and
leaves the run OPEN. `sprint sign --report RPTxxxx --principal "<name>"` is SEAL: the per-unit
rows, the terminal transitions, the cascades they imply, the run's signature and its outcome,
and then it stops. `--apply-signoff` exits 2 and names `sign` rather than surviving as an alias
that would keep the old path alive in every operator's fingers, help file and runbook row.

A signature nothing refuses to write over only ORDERS the work, so the seal is a transaction:
the principal is judged across the WHOLE batch before anything is written, a sealed run refuses
the transitions that would move the facts its page states, and a re-open is explicit, names the
report it breaks and KEEPS the signature it breaks.

## WHAT THE PAGE IS

One report of record per run, derived and never hand-authored. It opens with the sprint goal
verbatim before any figure. Every figure carries a source that must resolve to somewhere a
reader can actually go, and a section with no data reads NOT MEASURED by name rather than as a
zero. The cost row states what the token meter covers and names the sessions it does not, and
it now carries the delegated agent spend separately - supplied by each agent, never measured
here. The four DORA keys each state their mapping. And the page reads INVALIDATED once its
figures no longer re-derive from the tree.

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
