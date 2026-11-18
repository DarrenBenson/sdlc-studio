# EP0366: A run awaiting the operator signature no longer blocks the next, and a delegated signature is disclosed

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0729
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0729. Delivers the work CR0729 requested.

## Story Breakdown

- [ ] [US1290: A new run can be planned and opened while a closed run awaits signature, and status names each one waiting](../stories/US1290-a-new-run-can-be-planned-and-opened.md)
- [ ] [US1291: Sprint sign under delegation requires an accepted authorising decision id and records it in the signature block](../stories/US1291-sprint-sign-under-delegation-requires-an-accepted-authorising.md)
- [x] [US1292: The report page and the evidence pack state that a delegated signature was delegated and name its decision](../stories/US1292-the-report-page-and-the-evidence-pack-state.md)
- [ ] [US1293: The TRD records the deferred signature ruling as an ADR, the sprint pages describe it and RFC0060 D6 is closed](../stories/US1293-the-trd-records-the-deferred-signature-ruling-as.md)

## Acceptance Criteria (Epic Level)

- [ ] A new run can be planned and opened while an earlier closed run awaits signature, and status names every run awaiting signature
- [ ] sprint sign entered under delegation requires the id of an accepted decision that authorises the span, and refuses a delegated signature without one
- [ ] The signature block, the report page and the evidence pack each state that a delegated signature was delegated and name the authorising decision
- [ ] The TRD records the ruling as an ADR and RFC0060's open decision D6 is closed with a pointer to RFC0065

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
