# EP0192: The sprint report is one derived artefact, and the close refuses without it

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0505. Delivers the work CR0505 requested.

## Story Breakdown

- [ ] [US0569: the sprint report is DERIVED from the tree: planned against delivered, and scope creep as a number](../stories/US0569-the-sprint-report-is-derived-from-the-tree.md)
- [ ] [US0570: a unit dropped or held mid-sprint records the reason, so the report names it instead of losing it with the session](../stories/US0570-a-unit-dropped-or-held-mid-sprint-records.md)
- [ ] [US0571: a known issue carried past the close records its stop-ship ruling and who made it](../stories/US0571-a-known-issue-carried-past-the-close-records.md)
- [ ] [US0572: the close REFUSES on an unanswered compulsory item and names which one](../stories/US0572-the-close-refuses-on-an-unanswered-compulsory-item.md)

## Acceptance Criteria (Epic Level)

- [ ] There is ONE compulsory checklist per sprint, and it is a template that renders into a sprint report - the same document, not two artefacts to keep in step. Its sections are the questions this repo re-derives every run: planned vs delivered points, units DROPPED with the reason, SCOPE CREEP (artefacts filed that were not planned, counted and listed), the review that ran and by which seat, KNOWN ISSUES carried with their stop-ship ruling, and the sign-off record.
- [ ] Each compulsory item is DERIVED where it can be derived, and only asked where it cannot. Delivered points, filed-but-unplanned artefacts, the review records and the sign-off record are all already in the tree - a checklist that asks an agent to retype them will be filled in with what the agent remembers rather than what happened, which is the failure mode the derived index already exists to prevent.
- [ ] The close REFUSES on an unanswered compulsory item, naming it. A checklist nothing enforces is the state this CR is filed from: the seat ceremony was already compulsory in prose and was skipped without a warning.
- [ ] A known issue carried past the close records its STOP-SHIP RULING and who made it, so 'carried' and 'nobody looked' are distinguishable in the record - this batch carried eleven, one of them a shipped command that tracebacks on a default install, and that ruling existed only in conversation until it was written down by hand.
- [ ] Scope creep is reported as a NUMBER against the plan, not as a list to read: a sprint that filed 17 unplanned artefacts against 11 planned units should say so in one line, because that ratio is the signal and it is currently invisible.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
