# EP0228: Installed-copy drift is caught before the close, without weakening the close's backstop

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0528
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0528. Delivers the work CR0528 requested.

## Story Breakdown

- [ ] [US0735: Drift is reported at a point BEFORE the close, with the point chosen and priced](../stories/US0735-drift-is-reported-at-a-point-before-the.md)
- [ ] [US0736: The report NAMES the drifted files rather than a count](../stories/US0736-the-report-names-the-drifted-files-rather-than.md)
- [ ] [US0737: The two reported-not-failed states stay reported: no installed copy, and a pinned copy](../stories/US0737-the-two-reported-not-failed-states-stay-reported.md)
- [ ] [US0738: The `sprint close` installed-copy gate is UNCHANGED and still blocks](../stories/US0738-the-sprint-close-installed-copy-gate-is-unchanged.md)
- [ ] [US0739: Which shape was chosen - refuse, warn or mirror - is recorded as a decision with its reasoning](../stories/US0739-which-shape-was-chosen-refuse-warn-or-mirror.md)

## Acceptance Criteria (Epic Level)

- [ ] The drift between this repository's skill source and the installed copy is reported at a point BEFORE the close - the chosen point being priced by this request, with push as the candidate - so a fix cannot sit in force nowhere for the length of a run.
- [ ] The report names the drifted files, not a count: `forward-port --check` already does, and a signal that says only 'something differs' sends the reader to run the sweep to find out, which is the cost the check exists to avoid.
- [ ] The two states `forward-port --check` already reports rather than fails - no installed copy, and a copy holding a `.local/forward-port.pin` marker - stay reported rather than failed at the new point too, or a machine that deliberately does not mirror starts refusing work it has no stake in.
- [ ] The `sprint close` installed-copy gate is UNCHANGED and still blocks. Whatever is added earlier is a narrowing of the window, never a replacement for the backstop that has already proven it fires.
- [ ] Which shape was chosen - refuse, warn, or mirror - is recorded as a decision with its reasoning, because a warning nobody reads and a refusal everybody disables are different failures and the record must say which one was accepted.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
