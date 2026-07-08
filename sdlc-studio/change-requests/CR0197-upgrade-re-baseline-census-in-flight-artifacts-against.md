# CR-0197: Upgrade re-baseline: census in-flight artifacts against the capability delta

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** process

## Summary

`project upgrade` reports the project-level gap well (capability delta, auto-correctable
vs needs-judgement lanes, `provenance.adopt_after` era-gating) but never walks the
**non-terminal artifacts**. After an upgrade, incomplete stories and CRs were planned
under the old doctrine: no difficulty/tier stamps if routing post-dates the plan, no
plan-review verdict slot if that gate lands (CR0194), ACs written before Verify-line or
evidence-schema conventions, telemetry fields absent. Today the operator discovers each
gap one artifact at a time - usually as a surprise gate failure at the next transition,
or worse, not at all.

Add a re-baseline step to the upgrade workflow (extending `project_upgrade.py`): census
every non-terminal artifact, diff it against the capability delta, and report per-artifact
gaps in three buckets with era-gated policy:

- **Backfill (mechanical, applied on `--apply`):** stamps that are deterministic and
  read-only to compute now - e.g. `route.py estimate` difficulty on units lacking it,
  missing schema fields with safe defaults. Never invents history: telemetry and metrics
  start at the upgrade; no fabricated past rows.
- **Re-review queue (reported, never auto-run):** artifacts that would now match a gate's
  deterministic trigger but lack the corresponding verdict - e.g. an in-flight story with
  spec-citing ACs and no plan-review verdict once that gate exists. Policy: the new gate
  applies from the artifact's NEXT transition; completed transitions are never
  retroactively invalidated (the schema-v3 era-gating precedent). Un-started stories
  (Draft/Ready) are flagged cheap-to-re-plan; in-progress ones gate at their next
  transition.
- **Honest residual:** judgement gaps the tooling can only name (informal ACs, missing
  Verify lines) - already the needs-judgement lane, now itemised per artifact instead of
  as a category.

Not all incomplete stories need re-reviewing - the bucket assignment is deterministic
(status x capability-delta match), so the operator gets a bounded, prioritised list
rather than either extreme (silently grandfather everything / re-review everything).

**Design constraint:** TRD ADR-006 applies - the fire/skip trigger is deterministic; model judgement acts only inside a fired step.

## Open decisions (resolve at design)

- Home: a `project_upgrade.py` section, a `reconcile` lens (`reconcile detect --era`), or
  both sharing one helper - reconcile is the recurring cadence, upgrade is the one-shot.
- Whether the re-review queue writes a marker into each flagged artifact (visible in the
  file, survives the report) or lives only in the report/index.
- Interaction with `adopt_after`: one era watermark or per-capability watermarks (a
  project may adopt routing at v3.5 and plan-review at v4.0).

## Acceptance Criteria

- [ ] `project upgrade` dry-run lists every non-terminal artifact with its per-capability
      gaps, bucketed backfill / re-review / judgement; empty buckets print explicitly
- [ ] `--apply` performs only the mechanical backfill bucket; idempotent; a second run
      reports nothing to do
- [ ] New gates never retroactively invalidate a completed transition; enforcement
      attaches at the artifact's next transition and that policy is stated in
      reference-upgrade
- [ ] No fabricated history: telemetry/metrics fields absent before the upgrade remain
      absent for past events and begin recording forward
- [ ] Unit tests: bucket assignment per (status x delta) case, idempotency, and the
      era-gate boundary (a Done story is untouched; a Ready story is flagged)

## Evidence

- Raised from the N=5 close-out discussion (D0014 follow-ups): CR0194/CR0195 will create
  exactly this class of gap for every consuming project the day they ship; routing
  already did (units planned before the routing release carry no difficulty/tier stamps).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Filed from operator question at N=5 close-out |
