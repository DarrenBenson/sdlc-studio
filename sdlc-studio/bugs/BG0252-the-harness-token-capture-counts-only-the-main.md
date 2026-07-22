# BG0252: The harness token capture counts only the main thread, so a fan-out sprint publishes roughly a third of what it actually cost, labelled as the run's own spend

> **Status:** Fixed
> **Verification depth:** functional - reproduced through the capture itself (an open run with
> a main-thread delta and delegated totals recorded against it), then fixed red-to-green, then
> mutation-proven with 10 hand-applied mutants across `retro.py` and `lib/run_state.py`, all
> killed. The label is the load-bearing half, so it is pinned directly: a test asserts the
> basis no longer contains the words "own spend" and always contains "at least", and the row's
> Source cell reads `harness+supplied` when any part of the figure was supplied. The
> single-thread positive control is pinned too, so the new provenance cannot become the
> universal answer.
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py,.claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0236 made the close capture this run's DELTA from a baseline stamped at plan time, which was correct and is a real improvement. But `session_tokens` sums usage records from the session transcript, and subagent work is not recorded there. Measured on this transcript: 6,624,813 tokens of usage, of which sidechain records account for ZERO. Every delegated agent's spend is invisible. RUN-01KY321Q is the first run to close with an attributable figure, and that figure is 439,982 tokens - while the four cluster agents that did most of the building reported 198,734, 220,109, 163,373 and 205,618 between them, a further 787,834, with the closing review agent still running and uncounted. So the known true cost is at least 1,227,816 and the published number understates it by 64 per cent. The label is the defect: `run_attributed_tokens` returns a basis reading "RUN-xxxx's own spend: the current-session total N less the M on the meter when the run opened", which claims to be the run's cost and is in fact the run's MAIN-THREAD cost. This is the same family as BG0236 and BG0218 - a number correct about something narrower than its label - and it is more dangerous than either, because it looks like a successful measurement rather than an obvious absence. Concretely: at 18 points the published figure reads 24,443 tokens per point, 2.2 per cent under the 25,000 seed, which invites the conclusion that the seed is validated. The true rate is at least 68,212 per point, about 2.7 times the seed. The author computed and nearly reported the false calibration before checking the transcript for sidechain records.

## Steps to Reproduce

1. Run a sprint that delegates work to subagents. 2. Close it and read the captured token figure. 3. Sum the usage records in the session transcript, partitioning on the sidechain marker. Observed here: 6,624,813 total, 0 sidechain. 4. Compare the captured delta against the spend the subagents themselves reported. Observed: 439,982 published against at least 1,227,816 actually spent.

## Proposed Fix

First stop the label overclaiming, because that is cheap and makes the number honest today: a capture that cannot see delegated work must say it measures the main thread, not the run. Then decide whether the delegated spend can be recovered at all - subagent totals ARE reported back when each finishes, so a run could accumulate them as they land rather than trying to read them from a transcript that does not carry them. Whichever route, the retro and velocity row must distinguish a whole-run figure from a main-thread one, or the series will silently mix the two and every comparison across sprints will be between different quantities: a sprint built by one thread and a sprint built by five agents would be compared as though the numbers meant the same thing. Guard it with a test that records subagent spend against a run and asserts the published figure either includes it or is labelled as excluding it - never silent.

## Acceptance Criteria

- [x] **AC1:** The capture is published as a MAIN-THREAD measurement and a LOWER BOUND, never
      as the run's own spend.
      Pinned by `test_retro.TheCaptureMeasuresTheMainThreadAndSaysSo`.
- [x] **AC2:** A delegated agent's own reported total can be recorded against the run, is
      marked `supplied`, accumulates per agent, and survives the close and the archive.
      Pinned by `test_run_state.DelegatedSpendIsSuppliedNotMeasured`.
- [x] **AC3:** A published figure that includes a supplied half says so in the row's Source
      column, and a wholly main-thread capture does not.
      Pinned by `test_retro.TheCaptureMeasuresTheMainThreadAndSaysSo`.
- [x] **AC4:** The meter reader itself states that it sees only the main thread, so no caller
      can inherit the figure without the qualification.
      Pinned by `test_retro.test_the_meter_reader_says_it_sees_only_the_main_thread`.

## Resolution

The ruled fix, in four parts. The label was most of the defect, so most of the fix is the label.

1. **At the source.** `run_state.session_tokens` now states in its own basis that the sum is
   MAIN THREAD only and is therefore a lower bound - the transcript carries no sidechain usage
   record at all. Every caller inherits the sentence instead of having to know the fact.
2. **A place for the delegated half.** The run record gains `delegated_tokens`: one entry per
   agent, each stamped `supplied`, written by `run_state.record_delegated_tokens`. Supplied,
   never measured - nothing here read a meter. A non-positive or malformed total raises rather
   than being recorded as a zero somebody would later add into a total. The records survive
   `update`, `close_run` and the archive.
3. **The published figure.** `run_attributed_tokens` returns `measured_tokens` (the main-thread
   delta), `delegated_tokens` (the supplied sum), `delegated_records`, `lower_bound: True`, and
   a `tokens` that is their sum. Its basis reads "RUN-xxxx cost AT LEAST N" and names which
   half is measured and which is supplied. The old sentence - "RUN-xxxx's own spend" - is gone,
   and a test asserts it never comes back.
4. **The operator path and the record.** `accuracy --delegated-tokens N [--delegated-agent
   NAME]` records a delegated total against the open run before the capture reads it. A row
   carrying a supplied half is stamped `harness+supplied` in the Source column, and the
   velocity record's header now says that a `harness` figure is a lower bound and why, with the
   measured evidence (6,624,813 tokens of session usage, zero from sidechains).

Not fixed, and NOT claimed to be: nothing here recovers a delegated total nobody supplies. That
is the honest position - the transcript cannot see it - and it is exactly why the sum is
published as `>=` rather than `=`. Wiring the sprint runner to record each agent's reported
total as it lands belongs in `sprint.py`, which this unit does not own.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Fixed: main-thread measured + delegated supplied, published as a lower bound |
