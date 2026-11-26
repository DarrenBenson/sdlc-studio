# RFC-0069: What a long wait inside an agent costs once its prompt cache expires, and whether builders and round-two reviewers should avoid one

> **Status:** In Review
> **Decomposed-into:** EP0383
> **Date:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T21:34:17Z

## Summary

A builder waits 20 to 40 minutes on the full suite inside its own context, and a reviewer is resumed for round two after its unit's repair is built and landed, often an hour or more later. If the cache has expired by then, the next turn writes the whole context again: 158k to 226k tokens on average in run twenty-six (RPT0045), at $5 or $8 per million on Opus against $0.20 to read, 25 to 40 times the price. In run twenty-seven two builders' 40-minute suite runs timed out and the push gate judged the suite instead, so that wait bought nothing. The Claude-in-Foundry cost session recorded on 2026-11-24 (Controlling Claude Costs in Foundry) made the same point about switching models mid-session: each model keeps its own cache, so a switch writes the context again at 12.5 to 50 times the read price.

## Design Options

- **A. Measure first: the cost anatomy splits each agent's cache writes into growth (new turns) and re-writes after a gap longer than the cache lifetime, from the timestamps it already reads.**
- **B. A builder hands the full suite to the push gate and runs only the test modules its change selects.**
- **C. Round two goes to a fresh agent of the same seat, briefed with its own round-one verdict, instead of a resume. This needs a ruling, since `lane accept` takes a round-two verdict only from the reviewer whose REJECT stands.**
- **D. Keep resumes, but resume inside the cache lifetime, or use the one-hour cache where the wait is known to be long.**

## Recommendation

A first. B, C and D each trade cost against something (B against the builder's own evidence, C against the same-reviewer rule), and the size of the saving decides whether that trade is worth making.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: A. Measure first: the cost anatomy splits each agent's cache writes into growth (new turns) and re-writes after a gap longer than the cache lifetime, from the timestamps it already reads., B. A builder hands the full suite to the push gate and runs only the test modules its change selects., C. Round two goes to a fresh agent of the same seat, briefed with its own round-one verdict, instead of a resume. This needs a ruling, since `lane accept` takes a round-two verdict only from the reviewer whose REJECT stands. or D. Keep resumes, but resume inside the cache lifetime, or use the one-hour cache where the wait is known to be long. | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
