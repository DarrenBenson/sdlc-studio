# CR-0158: Tolerant convention layer: one classifier in lib, config-declared conventions, guarded normalised matching

> **Status:** Complete
> **Created:** 2026-07-05
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature
> **Implements:** RFC-0023 (Accepted, D0010)
> **Affects:** scripts/lib/ (new module), sdlc-studio/.config.yaml schema, reconcile.py, audit.py, sdlc_md.py callers

## Summary

Build the shared classification layer RFC-0023 recommends: a single `lib/` module
that answers "is this file an artifact?", "which header cell is the status
column?", and "does this text carry section X?" for every consumer
(reconcile, validate, audit, next_id, artifact scaffolding). Policy per D0010:
Option C as the structure, config-declared conventions (Option A) as the primary
mechanism, normalised matching (Option B) only where a synonym is unambiguous,
and existing exact guards (the Dependency-Status scavenge case) kept per-site.

CR-0154 (companion-doc detection) and CR-0155 (bug-readiness headings) land as
thin adoptions of this layer, not bespoke fixes. The write path is in scope:
`artifact.py new`/`batch` resolve the project's declared template before falling
back to the skill default, so the scaffold stops planting the mismatch the audit
then flags.

## Acceptance Criteria

- [ ] A `conventions` config block (status column aliases, companion suffixes,
      bug-ready section vocabularies, template overrides) parses from
      `sdlc-studio/.config.yaml`, every key defaulting to today's literal
      behaviour when absent (back-compat: an unconfigured project behaves
      identically to v3.4.0)
- [ ] One shared classifier module in `scripts/lib/` is the only place the
      conventions are interpreted; reconcile/validate/audit/next_id read
      through it (no second copy of any rule)
- [ ] Normalised matching applies only to declared-unambiguous cases
      (word-order-insensitive heading match, e.g. `Fix (proposed)` ==
      `Proposed Fix`); the reconcile `Dependency Status` exact guard is
      regression-pinned unchanged
- [ ] `artifact.py new --type bug` scaffolds a project-declared template when
      one is configured, skill default otherwise
- [ ] Unit tests cover config-present, config-absent, and malformed-config
      (fail loud, never guess) paths; mutation-checked
- [ ] `reference-*` docs describe the conventions block; CHANGELOG [Unreleased]

## Dependencies

| Artifact | Relationship |
| --- | --- |
| RFC-0023 | Implements (Accepted, D0010) |
| CR-0154 | Adopts this layer (companion detection) |
| CR-0155 | Adopts this layer (bug-readiness sections) |
| CR-0153 | Independent diagnostic point fix; its "found header X" message should name the conventions knob once this lands |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | sdlc | Created via `new` (deterministic) |
| 2026-07-05 | Claude (sprint planning) | Filled in as the RFC-0023 build vehicle per D0010: layer structure, config policy, guarded normalisation, write-path template resolution in scope |
| 2026-07-05 | Claude (sprint 2026-07-D) | Delivered in sprint 2026-07-D (24cfcab + a554fb5): lib/conventions.py layer, reconcile alias read AND write parity (critic F3), template write path; ConventionsError blocks the gate (critic F5) |
