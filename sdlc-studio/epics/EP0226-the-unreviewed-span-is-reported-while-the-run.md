# EP0226: The unreviewed span is reported while the run can still act on it

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0523
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0523. Delivers the work CR0523 requested.

## Story Breakdown

- [ ] [US0725: A unit reaching Review past the span threshold is REPORTED by the command that transitions it](../stories/US0725-a-unit-reaching-review-past-the-span-threshold.md)
- [ ] [US0726: The threshold is configurable, with a default DERIVED from what this repo actually does](../stories/US0726-the-threshold-is-configurable-with-a-default-derived.md)
- [ ] [US0727: `sprint status` states the open span without anyone running the close](../stories/US0727-sprint-status-states-the-open-span-without-anyone.md)
- [ ] [US0728: The report is advisory until its yield is measured, on the terms claim-drift and lane-check shipped under](../stories/US0728-the-report-is-advisory-until-its-yield-is.md)
- [ ] [US0729: A run with every unit covered stays silent, so the signal does not become noise](../stories/US0729-a-run-with-every-unit-covered-stays-silent.md)

## Acceptance Criteria (Epic Level)

- [ ] A unit reaching Review while the open unreviewed span exceeds a threshold is REPORTED by the command that transitions it, naming the span size and the `review-batch --open` invocation that closes it
- [ ] The threshold is configurable and has an honest default derived from what the repo actually does, not a number picked by assertion
- [ ] `sprint status` states the open span: how many delivered units no independent pass covers, so the answer is available without running the close
- [ ] The report is advisory first and its yield measured before it is allowed to block, on the same terms the claim-drift and lane-check lanes shipped under
- [ ] A run with every unit covered says so and stays silent, so the signal does not become noise that gets switched off

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
