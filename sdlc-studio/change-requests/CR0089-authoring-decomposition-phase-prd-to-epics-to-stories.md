# CR-0089: authoring decomposition phase PRD to epics to stories via shared core

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

**WS1 of RFC0019. Estimate: 5 points. Depends on CR0088.** The authoring phase: drive a PRD
to a reviewable backlog - decompose the PRD into epics, then epics into Ready stories - by
**reusing the existing generation core** (`epic`-from-PRD + `story`-from-epic, and
`cr action`'s decomposition), with stories created through the **batch** path (CR0078) so
ids/slugs/links/index are wired in one pass and delegated agents fill content only. Stops at
the `design` output (a reviewable backlog); never implements (D5: shared core, not a parallel
path; D7: stop at the backlog).

## Acceptance Criteria

- [ ] `sprint <prd.md> --goal design` produces epics from the PRD and Ready stories per epic,
      reusing the existing `epic`/`story` generation (no duplicated decomposition logic)
- [ ] stories are created via the batch path (contiguous ids, index rows, epic wiring in one
      pass); the run stops at a reviewable backlog with no implementation
- [ ] the backlog passes the closing consistency pass (CR0093) - reconcile drift 0, validate 0
- [ ] `--dry-run` previews the epic/story plan without writing
- [ ] unit tests cover the decomposition + batch wiring; CHANGELOG `[Unreleased]` entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
