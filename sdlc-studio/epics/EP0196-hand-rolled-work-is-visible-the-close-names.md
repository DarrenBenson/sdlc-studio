# EP0196: Hand-rolled work is visible: the close names what an agent did by hand instead of by tool

> **Status:** Draft
> **Derived Point Total:** 17
> **Parent:** CR0515
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0515. Delivers the work CR0515 requested.

## Story Breakdown

- [ ] [US0586: Every skill script records the artefact it touched and the action it performed, per run](../stories/US0586-every-skill-script-records-the-artefact-it-touched.md)
- [ ] [US0587: An artefact changed in the run diff with no tool provenance is reported by name at the close](../stories/US0587-an-artefact-changed-in-the-run-diff-with.md)
- [ ] [US0588: A hand-rolled action carrying a filed gap id is reported and does not block; one without is outstanding](../stories/US0588-a-hand-rolled-action-carrying-a-filed-gap.md)
- [ ] [US0589: A run that uses the tools throughout reports zero manual actions, so the detector cannot be one that never fires](../stories/US0589-a-run-that-uses-the-tools-throughout-reports.md)
- [ ] [US0590: The doctrine states the content-versus-tooling line and names reference-scripts.md as the pre-task catalogue](../stories/US0590-the-doctrine-states-the-content-versus-tooling-line.md)

## Acceptance Criteria (Epic Level)

- [ ] A run that hand-edits an artefact a tool could have changed reports that artefact by name at the close, derived from the run diff against the tool-use ledger rather than asked
- [ ] A hand-rolled action carrying a filed gap id is reported and does NOT block; one with no gap id is OUTSTANDING - the escape is a backlog entry, never a waiver
- [ ] The close reports a count of manual actions, and a run using the tools throughout reports zero - the positive control, so the item cannot be satisfied by a detector that never fires
- [ ] Replayed against RUN-01KYX375, the item names the six tools that run bypassed
- [ ] `reference-doctrine.md` states the content-versus-tooling rule, and `reference-scripts.md` is named as the pre-task catalogue, so a consuming project inherits both

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
