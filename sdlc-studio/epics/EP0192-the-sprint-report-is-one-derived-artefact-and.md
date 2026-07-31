# EP0192: The sprint report is one derived artefact, and the close refuses without it

> **Status:** Done
> **Derived Point Total:** 27
> **Parent:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0505. Delivers the work CR0505 requested.

## Story Breakdown

- [x] [US0569: the sprint report is DERIVED from the tree: planned against delivered, and scope creep as a number](../stories/US0569-the-sprint-report-is-derived-from-the-tree.md)
- [x] [US0570: a unit dropped or held mid-sprint records the reason, so the report names it instead of losing it with the session](../stories/US0570-a-unit-dropped-or-held-mid-sprint-records.md)
- [x] [US0571: a known issue carried past the close records its stop-ship ruling and who made it](../stories/US0571-a-known-issue-carried-past-the-close-records.md)
- [x] [US0572: the close REFUSES on an unanswered compulsory item and names which one](../stories/US0572-the-close-refuses-on-an-unanswered-compulsory-item.md)
- [x] [US0574: the checklist is one row per STAGE of the sprint cycle, each stating ran, not-run or waived](../stories/US0574-the-checklist-is-one-row-per-stage-of.md)
- [x] [US0575: the review row names who reviewed what, under which seat, over how many lenses](../stories/US0575-the-review-row-names-who-reviewed-what-under.md)
- [x] [US0576: impediments survive the close: blocked units and unresolved operator decisions are reported with what is in the way](../stories/US0576-impediments-survive-the-close-blocked-units-and-unresolved.md)

## The cycle this checklist covers

The compulsory set is not a list somebody thought of: it is one row per stage of the
loop this project already runs, so a stage that did not happen is visible rather than
inferred from its absence. The stages, in order, with the command that holds each:

| Stage | Held by | Authority for its row |
| --- | --- | --- |
| Index drift zero before the plan | `reconcile detect` (run by `sprint plan`) | derived |
| Sprint Goal stated and seat-reviewed BEFORE the plan | `sprint goal-review record` | derived |
| Batch groomed, nothing ungroomed admitted | `sprint breakdown`, `readiness check` | derived |
| Batch approved and the run opened | `sprint plan --write` | derived |
| Per-unit delivery under the Done gate | `conformance check`, `transition` | derived |
| Review at each delivery batch boundary | `sprint review-batch` | derived |
| Closing full-diff review | `critic sprint-review` | derived |
| Sprint Goal judged | `sprint goal-verdict` | derived |
| Retro plus the lessons loop | `gate --require-retro` | derived |
| Reviewer-of-record sign-off | `critic signoff` | derived |
| Handoff, when the run stopped short of its goal | `handoff generate` | derived |
| Known issues carried, each with a stop-ship ruling | the retro's carried-issues table | recorded |

Every row but the last is derived, because a checklist that asks an agent to retype what
the tree already holds gets filled in with what the agent remembers. The last cannot be
derived: a stop-ship ruling is a judgement, so it is recorded and its absence is reported.

One omission is deliberate rather than missing: there is no daily-stand-up row. The
per-unit lane already reports at each boundary, and a ceremony with no agent analogue
would be a row that is always waived, which teaches a reader to skim the column.

## Acceptance Criteria (Epic Level)

- [ ] There is ONE compulsory checklist per sprint, and it is a template that renders into a sprint report - the same document, not two artefacts to keep in step. Its sections are the questions this repo re-derives every run: planned vs delivered points, units DROPPED with the reason, SCOPE CREEP (artefacts filed that were not planned, counted and listed), the review that ran and by which seat, KNOWN ISSUES carried with their stop-ship ruling, and the sign-off record.
- [ ] Each compulsory item is DERIVED where it can be derived, and only asked where it cannot. Delivered points, filed-but-unplanned artefacts, the review records and the sign-off record are all already in the tree - a checklist that asks an agent to retype them will be filled in with what the agent remembers rather than what happened, which is the failure mode the derived index already exists to prevent.
- [ ] The close REFUSES on an unanswered compulsory item, naming it. A checklist nothing enforces is the state this CR is filed from: the seat ceremony was already compulsory in prose and was skipped without a warning.
- [ ] A known issue carried past the close records its STOP-SHIP RULING and who made it, so 'carried' and 'nobody looked' are distinguishable in the record - this batch carried eleven, one of them a shipped command that tracebacks on a default install, and that ruling existed only in conversation until it was written down by hand.
- [ ] Scope creep is reported as a NUMBER against the plan, not as a list to read: a sprint that filed 17 unplanned artefacts against 11 planned units should say so in one line, because that ratio is the signal and it is currently invisible.
- [ ] The compulsory set covers the FULL cycle, not just its close: every stage in the table above carries a row, a stage that did not run is named rather than omitted, and a guard fails when the cycle gains a stage the checklist has no row for. A checklist that only asks close-time questions certifies a close, not a sprint.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-30 | sdlc-studio | Planning pass: the checklist retargeted onto the existing `sprint_report.py` rather than a second report in `retro.py`; the compulsory set restated as one row per cycle stage; US0574-US0576 added for the stages the first four stories left uncovered (stage coverage, review attribution, impediments). 16 points to 27. |
