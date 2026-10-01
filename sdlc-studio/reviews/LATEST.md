<!-- close-status:begin -->
> **RUN-01M3T8N1 closed running.** 9 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3T8N1, the close seals first time: achieved.** Goal: "Maya signs, without a re-close,
> a report that checks VALID and names every operator ruling and carry." 9 of 9 units approved
> by one independent QA seat each, all in round 1. BG0865 was added mid-run on the operator's
> ruling, after BG0862's end-to-end test proved the signed page never stated a non-STOP-SHIP
> ruling. BG0841 and BG0860/BG0861 were deferred at the goal review.

## What landed

- **The seal no longer invalidates its own page (BG0848, the High).** The close settles every
  open unit span at one moment and meter reading, so `sign` moves nothing the page digests.
  The workaround RUN-01M3RPSK needed (units moved to terminal before the close) is retired.
- **The page names every ruling (BG0851, BG0865, BG0849).** A resolved decision counts as an
  operator ruling, every in-window forced override is listed (dropped units included), each
  known issue carries its retro ruling and who made it, and a graduation CR is ruled by class.
- **Carries close cleanly (BG0850, BG0829).** The rejecting reviewer discharges a carried unit
  past the cap, and the carried bug is filed with runnable criteria.
- **The close stops lying about approved bugs (BG0859)** and the retro scaffold names its run
  and carries the known-issues table (BG0826).
- **BG0862 proves it end to end**: one unstubbed close, sign and check, VALID first time;
  reverting any of seven fixes fails a named assertion.

## What is owed

- **Filed from this run:** BG0863 (an unreadable ledger drops status rows, a regression the
  reviewer ruled non-blocking), BG0864 (Fixed admits a bug whose Verify never ran), and Lows
  on CR0592. BG0841, BG0860 and BG0861 remain deferred.
- **Push** the close commits; the installed copy is forward-ported.
