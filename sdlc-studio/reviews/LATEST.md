<!-- close-status:begin -->
> **RUN-01M3Y7DP closed running.** 7 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3Y7DP, report honesty: achieved.** Goal: "Maya signs a sprint report whose delivery,
> cost and DORA figures match what the run actually did." 8 of 8 units approved by one
> independent QA seat each (BG0895 discharged after a carry at the cap); built in one lane, every
> unit's builder spend recorded through `lane return --tokens/--minutes`.

## What landed

- **Cost is measured per unit.** A lane brief and return open and close a unit's span (US0979);
  a lane return records the builder's token and minute totals, and the token ratio is withheld
  while any unit that did work lacks one (US0980). This run's page counts the builders' and reviewers' spend in its Tokens row
  where RPT0014 read 0.2x from the orchestrator's meter alone.
- **Delivery is counted honestly.** A carry discharged inside the run counts as delivered, read
  from PREPARE's frozen gate (BG0890); a batch finding no longer moves a signed page, and the
  close's checklist agrees with the page on a first close and on a re-close (BG0895).
- **DORA and calibration.** Time to restore pairs a red streak with the first success created
  after it, floored at zero, median across incidents (BG0891, D0304); velocity rows keep their
  model, and RETRO0121-RETRO0129 were re-recorded (BG0892, D0307).
- **The page reads true.** The header names its window end (BG0893); a close gap holds only a
  step's failures (BG0894).

## What is owed

- **Filed from this run, all groomed:** BG0898-BG0910 (Lows: residue and coverage from the
  reviews, plus the minutes-rate fallback BG0907 and the wall-versus-active minutes ratio BG0898).
- Every seat ruling is in the decision log (D0298-D0308), per D0295.
