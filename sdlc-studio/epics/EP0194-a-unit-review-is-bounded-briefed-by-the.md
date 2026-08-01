# EP0194: A unit review is bounded, briefed by the tool, and blocks only on what the unit broke

> **Status:** Draft
> **Derived Point Total:** 23
> **Parent:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0512. Delivers the work CR0512 requested.

## Story Breakdown

- [x] [US0577: A recorded review verdict carries the provenance of the brief it was given, so a hand-written prompt is detectable](../stories/US0577-a-recorded-review-verdict-carries-the-provenance-of.md)
- [x] [US0578: Recording a verdict with no brief provenance is REFUSED, and the refusal names critic.py brief](../stories/US0578-recording-a-verdict-with-no-brief-provenance-is.md)
- [x] [US0579: Every finding on a verdict is classified REGRESSION, NEW or PRE-EXISTING, and an unclassified verdict is refused](../stories/US0579-every-finding-on-a-verdict-is-classified-regression.md)
- [x] [US0580: Only REGRESSION and NEW hold a gate: a PRE-EXISTING finding is reported and does not block](../stories/US0580-only-regression-and-new-hold-a-gate-a.md)
- [ ] [US0581: A finding matching an open Bug or CR is annotated with that id automatically and never blocks](../stories/US0581-a-finding-matching-an-open-bug-or-cr.md)
- [x] [US0582: The shipped doctrine states the review scope rule, so a consuming project inherits the bound and not just the ceremony](../stories/US0582-the-shipped-doctrine-states-the-review-scope-rule.md)

## Acceptance Criteria (Epic Level)

- [ ] A seat brief produced by any path other than `critic.py brief` is refused, and the refusal names the command.
- [ ] A recorded review verdict carries a per-finding classification, and a verdict whose findings are unclassified is refused.
- [ ] A PRE-EXISTING finding is reported in the verdict and does NOT appear in the blocking set, proven by a test whose only variable is whether the defect predates the run's base ref.
- [ ] A finding whose text matches an open Bug/CR is annotated with that id and does not block.
- [ ] A genuine REGRESSION still blocks - the positive control, so the change cannot be satisfied by a gate that stopped blocking.
- [ ] Applied retrospectively to the RUN-01KYX375 review record, the blocking-finding count falls, and the measured before/after is recorded rather than asserted.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
