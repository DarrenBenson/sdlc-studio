# BG0598: the plan's BUILT-NOT-CLOSED exclusion reads verifier greens and not the verdict ledger, so a unit with an unanswered REJECT is priced at zero

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Found by the product and engineering seats independently during the adversarial goal review of 2026-08-19; the classifier and the ledger record were then read directly to confirm the mechanism.
> **Created:** 2026-08-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-18T20:35:22Z

## Summary

`sprint._built_not_closed` classes a unit as BUILT-NOT-CLOSED when it is non-terminal, not depth-retracted, and all its executable criteria pass. It never asks the critic ledger. A unit whose adversarial review REJECTED it - repeatedly, with the REJECT unanswered - therefore reads as built work needing only a close, and `_token_forecast` removes its points from the batch total. The unit with the worst convergence record in a batch is the one the forecast prices at nothing.

## Steps to Reproduce

Measured 2026-08-19 while planning a 30-unit batch. `sprint.py plan --worklist <file> --goal done` prints `excluded from the build forecast (BUILT-NOT-CLOSED, close them): BG0592 - this removes 3 point(s), so the forecast prices 95 point(s) of a batch carrying 98 priced point(s)`. `critic.py show --unit BG0592` returns `verdict: REJECT`, reviewer `qa seat (subagent, repair round)`, five open issues, and the line `repair: none recorded - this REJECT is unanswered`. `sdlc-studio/reviews/LATEST.md` records the same unit as rejected four times and escalated twice, with the repair not converging. Two records of one unit's state disagree, and the forecast is computed from the more optimistic.

## Proposed Fix

Ask the ledger. A unit carrying an unanswered REJECT is not built - it is work whose remaining cost is a repair round, which the fixed-term half of the forecast prices for the batch and not for the unit. `depth_retracted` is already consulted for exactly this reason, and its comment gives the argument verbatim: the verify-report may still read green while the review has judged the evidence meaningless, so the retraction must outrank it. An unanswered REJECT is the same shape and is not asked. Either exclude it from BUILT-NOT-CLOSED, or report it in a third class - reviewed and rejected - so the exclusion sentence cannot read as an instruction to close it.

## Acceptance Criteria

- [ ] **AC1** Given a unit carrying an unanswered REJECT in the critic ledger, when `sprint._built_not_closed` judges it, then it returns False - a unit no reviewer has approved is not built work awaiting a close
- [ ] **AC2** Given a unit whose REJECT carries a recorded repair answering it, when `_built_not_closed` judges it, then verifier greens decide exactly as they do today - the control proving the ledger read discriminates rather than excluding every unit that was ever reviewed
- [ ] **AC3** Given a batch holding a unit with an unanswered REJECT, when `_token_forecast` accumulates the batch total, then that unit's points are counted IN it - the exclusion must be decided in ONE place, so a second accumulation path that short-circuits on green verifiers before consulting `_built_not_closed` cannot restore the defect behind the fix
- [ ] **AC4** Given that same unit, when the plan reports it, then it is named in a class of its own - reviewed and rejected, not built - so the exclusion sentence cannot read as an instruction to close a unit nobody approved
- [ ] **AC5** Given a fixture workspace passed by `--root`, holding one unit with all criteria green and an unanswered REJECT and one with all criteria green and no verdict at all, when `sprint.py plan --worklist` is driven through the shipped CLI by subprocess from a DIFFERENT working directory, then the printed forecast prices the first and excludes the second - a ledger path resolved from the process cwd rather than from `--root` passes an in-process test and fails this one
- [ ] **AC6** Given a DIRECTORY at the critic ledger's path - a shape that raises for every user, where `chmod 000` is a no-op when the suite runs as root - when `_built_not_closed` judges, then it fails closed and treats the unit as unbuilt; a MISSING ledger is the no-verdict case and must not satisfy this criterion

## Impact

The exclusion sentence tells the operator to `close them`, about a unit no reviewer has approved. The forecast under-prices the batch by exactly the units least likely to land, which is the wrong direction for a planning figure to be wrong in. It is also the shape this repository files hardest against: a count that survives because the artefacts it contradicts were never read.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, drop the ledger read from `_built_not_closed` | Given a unit carrying an unanswered REJECT in the critic ledger, when `sprint._built_not_closed` judges it, then it returns False - a unit no reviewer has approved is not built work awaiting a close |
| AC2 | in `sprint.py`, widen the check to exclude any unit carrying a verdict | Given a unit whose REJECT carries a recorded repair answering it, when `_built_not_closed` judges it, then verifier greens decide exactly as they do today - the control proving the ledger read discriminates rather than excluding every unit that was ever reviewed |
| AC3 | in `sprint.py`, revert the forecast to subtract those points | Given a batch holding a unit with an unanswered REJECT, when `_token_forecast` accumulates the batch total, then that unit's points are counted IN it - the exclusion must be decided in ONE place, so a second accumulation path that short-circuits on green verifiers before consulting `_built_not_closed` cannot restore the defect behind the fix |
| AC4 | in `sprint.py`, merge the new class back into the existing sentence | Given that same unit, when the plan reports it, then it is named in a class of its own - reviewed and rejected, not built - so the exclusion sentence cannot read as an instruction to close a unit nobody approved |
| AC5 | in `test_sprint.py`, clone one fixture unit over the other | Given a fixture workspace passed by `--root`, holding one unit with all criteria green and an unanswered REJECT and one with all criteria green and no verdict at all, when `sprint.py plan --worklist` is driven through the shipped CLI by subprocess from a DIFFERENT working directory, then the printed forecast prices the first and excludes the second - a ledger path resolved from the process cwd rather than from `--root` passes an in-process test and fails this one |
| AC6 | in `sprint.py`, delete the explicit ledger-path probe and let `read_text_safe` return empty | Given a DIRECTORY at the critic ledger's path - a shape that raises for every user, where `chmod 000` is a no-op when the suite runs as root - when `_built_not_closed` judges, then it fails closed and treats the unit as unbuilt; a MISSING ledger is the no-verdict case and must not satisfy this criterion |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
