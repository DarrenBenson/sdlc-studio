# EP0373: Existing behaviour is pinned by a test before a story changes it

> **Status:** Draft
> **Derived Point Total:** 7
> **Parent:** CR0736
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0736. Delivers the work CR0736 requested.

## Story Breakdown

- [ ] [US1307: `sprint plan` names each source file in a unit's Affects that no test reaches within one hop, never reporting a file the unit creates](../stories/US1307-sprint-plan-names-each-source-file-in-a.md)
- [ ] [US1308: `plan.unpinned_code` (warn by default, refuse) decides whether a batch with unpinned files is planned](../stories/US1308-plan-unpinned-code-warn-by-default-refuse-decides.md)
- [ ] [US1309: The brownfield runbook has a pin-behaviour stage before the first code change, with its done test](../stories/US1309-the-brownfield-runbook-has-a-pin-behaviour-stage.md)

## Acceptance Criteria (Epic Level)

- [ ] `sprint plan` names, per unit, each source file in its Affects that no test file imports directly or through one hop in the repo map
- [ ] With `plan.unpinned_code: refuse` the batch is refused naming those files; with warn, the default, it is planned and the warning is printed
- [ ] A file the unit itself creates is never reported as unpinned
- [ ] The brownfield runbook has a numbered stage, before the first code change, that pins existing behaviour with tests and states how to tell it is done

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
