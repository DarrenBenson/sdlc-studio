# CR-0138: make a mixed bugs + CRs tranche a first-class sprint batch

> **Status:** Approved
> **Created:** 2026-07-04
> **Created-by:** field report (a consuming project's backlog-clear sprint, 2026-07-04)
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** scripts/sprint.py, scripts/audit.py, scripts/conformance.py, help/sprint.md, reference-sprint.md
> **Depends on:** -
> **Created-by:** sdlc-studio remake (backfilled)

## Summary

The most common maintenance sprint is "clear the backlog" - open bugs plus proposed CRs in one
tranche. Today that batch is not expressible: `sprint.py plan` takes exactly one of
`--bugs | --crs | --stories` (mutually exclusive), so the operator loop runs the planner twice,
hand-merges the two plans (including recomputing dependency waves across the type boundary, where
edges like "CR depends on BG" are common), and `--write` persists whichever single-query plan ran
last. The documentation compounds it: `help/sprint.md` and `reference-sprint.md` both name "a
worklist/tranche file" as a batch source, but the script has no such input.

Three follow-on gaps surfaced in the same field run:

- **Ordering has no common scale across types.** By design bugs order by `Severity`
  (Critical/High/Medium/Low) and CRs by `Priority` (P1-P4); in a merged batch the two vocabularies
  are not comparable, so the operator loop had to invent its own combined order.
- **`audit.py check` unmet-deps is batch-blind.** A dependency that sits in the SAME tranche, wave-
  ordered ahead of its dependent, still reports `NOT READY ... unmet-deps` - the exact situation the
  planner's dependency waves exist to create. The operator has to overrule the auditor for doing the
  plan's job correctly.
- **`conformance.py check` judges only stories.** A bugs + CRs tranche therefore ships with no
  per-unit deterministic conformance at all; the loop leans entirely on the critic and the gate,
  and nothing states that scoping.

## Acceptance Criteria

- [ ] `sprint.py plan` accepts a composed batch: either combinable queries
      (`--bugs Open --crs Proposed`) or the already-documented worklist file (ids one per line);
      one merged, dependency-waved plan comes out, and `--write` persists that merged plan
- [ ] cross-type ordering uses one documented scale (map bug Severity and CR/story Priority onto a
      shared weight; the mapping is stated in reference-sprint.md, not implicit)
- [ ] `audit.py check` over a plan/batch treats a dependency satisfied by an earlier wave of the
      same batch as `sequenced-in-batch` (informational), reserving `unmet-deps` for referents
      genuinely outside the tranche and not delivered
- [ ] either `conformance.py check` judges bug and CR units (they carry checkable AC / verification
      sections), or the gate output and reference-sprint.md state plainly that conformance is
      story-scoped so a bug/CR tranche relies on critic + gate
- [ ] `help/sprint.md` / `reference-sprint.md` worklist-file wording matches what the script
      actually accepts; `CHANGELOG.md` `[Unreleased]` ([[LL0004]])

## Out of Scope

- WSJF seat scoring changes (the existing degrade-to-priority path is fine).
- Epic-scoped story batches (already supported via `--epic`).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | field | Filed from a consuming project's mixed backlog-clear sprint (two plans hand-merged; auditor overruled twice; conformance silent on all 8 units) |
