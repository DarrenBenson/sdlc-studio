# CR-0067: deploy workflow gate to operator-triggered deploy to verify tier to surface rollback (RFC0013 WS2)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

RFC0013 WS2. The `deploy` workflow + `deploy.py preflight` helper: gate -> operator hand-off -> verify tier -> surface rollback. Orchestrate-only; the skill never executes the deploy/rollback and never deploys inside autosprint.

## Acceptance Criteria

- [x] `scripts/deploy.py preflight` runs the gate, emits readiness + the operator hand-off, never executes a deploy (executes=False); exit 1 when the gate is red
- [x] `reference-deploy.md` + `help/deploy.md` document the workflow and the safety stance (stop-condition; never autonomous)
- [x] SKILL.md routes `deploy` (type table + Progressive Loading Guide); reference-scripts.md + help/references.md index the new files
- [x] tests cover ready/not-ready/handoff/never-executes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
