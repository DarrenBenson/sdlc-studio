# EP0363: The disclosure lint lane fails when a finding appears that its committed baseline does not hold

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0725
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0725. Delivers the work CR0725 requested.

## Story Breakdown

- [ ] [US1285: The disclosure lane reads a committed baseline, fails on a new finding and prints one line when nothing is new](../stories/US1285-the-disclosure-lane-reads-a-committed-baseline-fails.md)
- [ ] [US1286: The disclosure baseline may only shrink, and the TSD rows say the lane fails on a rise against it](../stories/US1286-the-disclosure-baseline-may-only-shrink-and-the.md)

## Acceptance Criteria (Epic Level)

- [ ] A committed baseline under tools/ records the current disclosure findings by kind and name, and the `lint:disclosure` lane exits non-zero when a finding appears that the baseline does not hold
- [ ] The lane prints one summary line when the findings equal the baseline, and lists only the findings that are new
- [ ] tools/tests/`test_baselines_only_shrink.py` covers the new baseline, so a commit that grows it fails
- [ ] The TSD rows for the disclosure lane and for the progressive-disclosure requirement say the lane fails on a rise against its baseline, and the requirement row names the lane beside `check_budgets.py`

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
