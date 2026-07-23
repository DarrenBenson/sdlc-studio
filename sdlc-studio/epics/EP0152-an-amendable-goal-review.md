# EP0152: An amendable goal review

> **Status:** Draft
> **Derived Point Total:** 7
> **Parent:** CR0408
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0408. Delivers the work CR0408 requested.

## Story Breakdown

- [ ] [US0402: an amendment carries forward the seats it satisfies and re-consults only the rest, recording the prior wording and the requesting seat](../stories/US0402-an-amendment-carries-forward-the-seats-it-satisfies.md)
- [ ] [US0403: a material change still invalidates every verdict, the distinction an operator declaration, recorded](../stories/US0403-a-material-change-still-invalidates-every-verdict-the.md)

## Acceptance Criteria (Epic Level)

- [ ] A goal can be AMENDED against a recorded review, carrying forward the verdicts of seats whose stated position the amendment satisfies, and requiring only the seats it does not.
- [ ] An amendment records the previous wording and which seat asked for the change, so the trail shows the goal was improved rather than replaced.
- [ ] A change that is NOT an amendment - a materially different goal - still invalidates every verdict, exactly as today. Where the distinction cannot be made mechanically it is the operator's declaration, recorded, not the tool's guess.
- [ ] The staleness protection is unchanged: a verdict from a previous sprint can never discharge a current goal, amendment or not.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
