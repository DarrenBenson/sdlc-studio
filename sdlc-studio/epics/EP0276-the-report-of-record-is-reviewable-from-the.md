# EP0276: The report of record is reviewable from the committed tree and states its cost in money

> **Status:** Draft
> **Derived Point Total:** 15
> **Parent:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0610. Delivers the work CR0610 requested.

## Story Breakdown

- [ ] [US0997: A report the close files cites the committed run record, never .local/run-state.json](../stories/US0997-a-report-the-close-files-cites-the-committed.md)
- [ ] [US0998: The committed run record names its sprint plan by digest, not by a .local path](../stories/US0998-the-committed-run-record-names-its-sprint-plan.md)
- [ ] [US0999: A delegated agent's token total records the model that spent it](../stories/US0999-a-delegated-agent-s-token-total-records-the.md)
- [ ] [US1000: The cost section states the run's cost in money from a pricing snapshot frozen at the close](../stories/US1000-the-cost-section-states-the-run-s-cost.md)
- [ ] [US1001: The lane-yield appendix is read from the committed run record, as the close froze it](../stories/US1001-the-lane-yield-appendix-is-read-from-the.md)

## Acceptance Criteria (Epic Level)

- [ ] Every figure in a newly filed report cites a committed file (the RUN record or a committed digest) as its source, never a `.local/` path
- [ ] The RUN record carries a committed plan digest instead of a `.local/sprint-plan.json` path
- [ ] The cost section carries an optional pricing snapshot (model, price, currency, date) and money figures computed from it, and an unpriced model is listed as unpriced, never zero
- [ ] Reports filed before the change still check VALID

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
