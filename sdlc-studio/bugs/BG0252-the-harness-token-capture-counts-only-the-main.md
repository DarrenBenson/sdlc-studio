# BG0252: The harness token capture counts only the main thread, so a fan-out sprint publishes roughly a third of what it actually cost, labelled as the run's own spend

> **Status:** Open
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
