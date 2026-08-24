# EP0218: The plan review binds where the code is, so a unit takes one review round instead of two

> **Status:** Draft
> **Derived Point Total:** 24
> **Parent:** CR0555
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0555. Delivers the work CR0555 requested.

## Story Breakdown

- [ ] [US0685: The entry gate keeps the demand that a test plan EXISTS and drops the demand that a seat has approved it](../stories/US0685-the-entry-gate-keeps-the-demand-that-a.md)
- [ ] [US0686: The entry refusal names WHEN the independent approval will be demanded, so the move is not a silent relaxation](../stories/US0686-the-entry-refusal-names-when-the-independent-approval.md)
- [ ] [US0687: The terminal transition demands the independent plan-review approval and refuses without one exactly as entry does today](../stories/US0687-the-terminal-transition-demands-the-independent-plan-review.md)
- [ ] [US0688: The plan review and the delivery review are carried in ONE brief, so a unit takes one round where it took two](../stories/US0688-the-plan-review-and-the-delivery-review-are.md)
- [ ] [US0689: The move binds behind the existing dated cutoff, so a project that has not adopted it is unchanged and no backlog is retro-refused](../stories/US0689-the-move-binds-behind-the-existing-dated-cutoff.md)
- [ ] [US0690: The close names which units had the approval demanded at terminal and which the cutoff exempted](../stories/US0690-the-close-names-which-units-had-the-approval.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a unit entering implementation, when the gate runs, then a `## Test Plan` is still REQUIRED and its absence still refuses - the authoring-time rule is untouched at every band
- [ ] Given that same unit entering implementation, when the gate runs, then an independent plan-review approval is NOT demanded there, and the refusal message says when it will be
- [ ] Given a unit reaching a terminal status, when the gate runs, then the independent plan-review approval IS demanded, and a unit without one is refused exactly as it is refused at entry today
- [ ] Given the plan review and the delivery review now binding at the SAME point, when a reviewer is briefed, then both are carried in one brief, so a unit takes one round where it took two - this is the saving the move buys, and it needs no band at all
- [ ] Given a project that has not adopted this, when it transitions a unit, then behaviour is unchanged - the move is behind the same dated cutoff the existing gate uses, so an existing backlog is not retro-refused
- [ ] Given the close, when it reports, then it names units whose plan approval was demanded at terminal and those exempted by the cutoff, so the move is visible rather than silent

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Created via `new` (deterministic) |
