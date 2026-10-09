# EP0283: Grooming done before minting survives onto the stories refine mints

> **Status:** Draft
> **Parent:** CR0628
> **Derived Point Total:** 12
> **Parent:** CR0618
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0618. Delivers the work CR0618 requested.

## Story Breakdown

- [ ] [US1025: Refining a request into one story carries each criterion's own Given, When, Then and Verify lines onto its AC](../stories/US1025-refining-a-request-into-one-story-carries-each.md)
- [ ] [US1026: refine apply --breakdown mints each story with the persona, user story and criteria its entry carries](../stories/US1026-refine-apply-breakdown-mints-each-story-with-the.md)
- [ ] [US1027: A breakdown entry artifact.py new would refuse is refused before anything is minted, naming the story](../stories/US1027-a-breakdown-entry-artifact-py-new-would-refuse.md)
- [ ] [US1028: A breakdown entry's depends_on and notes land on the story refine mints](../stories/US1028-a-breakdown-entry-s-depends-on-and-notes.md)

## Acceptance Criteria (Epic Level)

- [ ] `refine apply --breakdown` accepts, per story, the fields `artifact.py new --type story` accepts (at least persona, as/`i_want`/`so_that`, acs with verify, `depends_on`, notes) and mints each story with them rendered as `artifact new` renders them
- [ ] A story field `artifact new` would refuse is refused by refine before anything is minted, naming the story

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
