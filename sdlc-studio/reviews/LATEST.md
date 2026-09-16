<!-- close-status:begin -->
> **RUN-01M2JA6J closed goal-reached.** 23 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> Closing review of record: RETRO0117 (`sdlc-studio/retros/RETRO0117-run-01m2ja6j-a-sprint-that-ends-with-nothing.md`).
> **Run of record:** RUN-01M2JA6J - a sprint that ends with nothing unanswered. Twenty-three
> units: 18 bugs to Fixed and 5 stories to Done, 70 plan-review verdicts and 48 delivery
> verdicts, and a corpus-verify lane that passes in CI against a baseline measured in CI.

## THE HEADLINE: A RUN CAN NO LONGER END OVER A QUESTION NOBODY ANSWERED

Five stories closed the routes by which a run could end quietly. An unfinished batch unit now
holds the close through its stop-ship step and names where its findings went (US0626). No story
or bug reaches Done or Fixed over a delivery REJECT whose findings were neither filed nor
repaired (US0627). A unit closed over a REJECT names, in its own record, the artefact its
findings were filed to (US0628). Every other route that ends a run - `stop`, `file-and-close`,
the boundary stop, the handoff - reads the same predicate as the close, and `stop --force`
records what it waived (US0823). The doctrine states the rule, the one store a stop-ship ruling
lives in, and who rules it (US0625).

## WHAT THE CORPUS LANE WAS ACTUALLY SAYING

BG0676 is the unit the whole batch was ordered around. The scheduled lane had been red on main
at 40 red criteria against a baseline of 20, and every one of the 21 it named as new passed on a
developer machine. It was not a corpus regression: the job installed no `coverage`, cloned one
commit deep, and gave every verifier gate.py's 120 s default while its slowest criterion needs
136. With those three corrected the same lane reads 19, one fewer than the baseline it started
from, and that improvement is BANKED rather than left to the tolerance.

The number was measured three times in CI before it was written down, and the reviews found the
cap before the lane did: the job's own ceiling was 90 minutes against a pass that now takes 85.6,
and a job killed at its cap is marked failure, indistinguishable from the red it exists to
report. That is BG0676's own defect class, and it was caught inside BG0676's own fix.

## WHAT THE REVIEWS COST AND BOUGHT

Plan review ran to 70 verdicts, 47 of them REJECT, before a line of code; one unit was rejected
five times. Delivery review, capped at two rounds by D0146, ran to 48 verdicts with 4 REJECTs,
and every one of the four was real: two regressions the authors' own suites passed, and a pair
of surviving mutants that would have restored the very defect the unit was fixing. D0204 now
caps plan review at three rounds, and CR0578 will encode it.

One stakeholder consult, run only because the operator asked when personas are consulted, found
the batch's largest design gap in a single pass: nothing checks who wrote a stop-ship ruling, so
the session that did the work can release its own hold (CR0571). Seventy seat verdicts had not
raised it. RFC0058 decides where that input belongs.

## WHAT IS OWED

- **Nothing is unanswered.** Every open finding this run filed carries a ruling in RETRO0117's
  carried table, made by the operator at the close review.
- **32 findings were filed at the close** - BG0690 to BG0709, CR0579 to CR0586, and three Lows
  folded into CR0511 - each one deferred, none worked inside the close.
- **The test-cost work is filed and measured, not asserted**: CR0584 (386 criteria select a whole
  test module, which both over-claims and costs most of the 84-minute corpus pass), CR0585 (shard
  a serial lane whose criteria are independent), CR0586 (module-alone pays 551 s of every 749 s
  push). Read CR0584 first: it is a quality repair that happens to be the largest speed-up.
- **Two ceilings sit inside their 5% tolerance** and will redden main on the next line added to
  either: `reference-config.md` at 104.89% and `reference-review.md` at 100.49%. This run learned
  that the hard way - `reference-sprint.md` crossed its own ceiling and turned main red.
- **BG0709 is the one to read next.** The pre-push red-main check trusts the forge's ordering,
  and a stale row had it demand acknowledgement of a run from July while main was green. Taking
  the printed remedy would have banked a false "red read" and inverted D0181.
