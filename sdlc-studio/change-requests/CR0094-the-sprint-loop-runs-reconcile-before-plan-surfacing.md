# CR-0094: the sprint loop runs reconcile before plan, surfacing drift before selection

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

**Estimate: 2 points.** The sprint planner reads each artifact's `Status` straight from its
file to select the batch, so a drifted index/status silently produces a plan built on shaky
state. Make the loop **run `reconcile` before `plan`** (operator rule, 2026-06-24): step 0 of
the loop reconciles, surfacing any mechanical drift before a batch is selected. Caveat to
document: reconcile catches **mechanical** drift (index vs file, counts, orphans), not
**semantic** staleness (a story whose feature shipped under a different artifact - the stale
v2.0 Ready stories) - that still needs the tranche audit + human grooming.

## Acceptance Criteria

- [ ] `reference-sprint.md` documents "reconcile (and groom) before plan" as step 0 of the loop,
      with the mechanical-vs-semantic caveat
- [ ] `sprint plan` runs `reconcile detect` first and surfaces drift: warns by default, refuses
      under `--strict` (so a plan is never built on a stale census)
- [ ] the check reuses `reconcile` (no new drift logic); 0-drift is silent
- [ ] unit test: a seeded index drift makes `plan --strict` refuse; CHANGELOG entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
