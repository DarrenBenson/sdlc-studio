# EP0240: An exemption reason is judged on meaning, not on character count

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0553
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0553. Delivers the work CR0553 requested.

## Story Breakdown

- [ ] [US0789: A reason carrying no distinct meaning-bearing tokens is REFUSED however long it is](../stories/US0789-a-reason-carrying-no-distinct-meaning-bearing-tokens.md)
- [ ] [US0790: A reason that is mostly the criterion's own words returned to it is refused as a restatement](../stories/US0790-a-reason-that-is-mostly-the-criterion-s.md)
- [ ] [US0791: One reason repeated verbatim across several criterion ids is refused](../stories/US0791-one-reason-repeated-verbatim-across-several-criterion-ids.md)
- [ ] [US0792: The number of existing exemptions the tightened floor newly refuses is REPORTED before it blocks](../stories/US0792-the-number-of-existing-exemptions-the-tightened-floor.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a declared exemption reason of twelve or more characters carrying no distinct meaning-bearing tokens, when the exemption is read, then it is REFUSED - the paired control being a short but genuine reason, which must still pass
- [ ] Given a reason that is mostly the criterion's own words returned to it, when the exemption is read, then it is refused as a restatement, on the same overlap test the test-plan rows already use
- [ ] Given one reason repeated verbatim across several criterion ids, when the exemption is read, then it is refused, because that is the shape an author reaches for when exempting a batch wholesale
- [ ] Given the existing corpus, when the tightened floor runs over it, then the number of exemptions it newly refuses is REPORTED before the check is allowed to block, so the change earns its place on a measurement rather than on assertion

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
