# EP0209: The reviewer of record can be a named seat, and the operator leads from a derived summary

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0532
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0532. Delivers the work CR0532 requested.

## Story Breakdown

- [ ] [US0643: A seat may sign only work it neither authored nor adversarially reviewed - three distinct contexts, enforced](../stories/US0643-a-seat-may-sign-only-work-it-neither.md)
- [ ] [US0644: The sign-off record states that a seat signed and names it, so no reader mistakes it for a human](../stories/US0644-the-sign-off-record-states-that-a-seat.md)
- [ ] [US0645: The operator summary is derived from the record, never composed by the signing seat](../stories/US0645-the-operator-summary-is-derived-from-the-record.md)

## Acceptance Criteria (Epic Level)

- [ ] Three distinct contexts are enforced, not requested: the signing seat is neither the author nor the seat that ran the adversarial pass, and the existing self-approval guard refuses a sign-off that collapses any two of them.
- [ ] A sign-off records WHO judged and in what capacity, so no reader can mistake an AI seat's signature for a human's - the record says `seat` and names it, and a consuming project reading the ledger can filter on it.
- [ ] The operator summary is DERIVED from the record - what shipped, what was rejected and why, what is carried and where it is filed, what it cost - and is not prose the signing seat composes about its own decision.
- [ ] The summary names the judgements the operator is most likely to want to overturn, so leading is a bounded act rather than re-reading the whole batch.
- [ ] A reversal path exists and is exercised by a test: the operator rejects a seat's sign-off, and the affected units return from Done to Review with the reversal recorded against the seat that signed.
- [ ] Which work a seat may sign is bounded by a declared policy rather than by judgement at the moment of signing, and the shipped default keeps product-shaped rulings - a criterion that cannot be made decidable, whether a feature may ship absent - with the human.
- [ ] A run that closes on a seat's sign-off is indistinguishable in the close chain from one closed on a human's, EXCEPT in the record - so no second code path exists to drift.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
