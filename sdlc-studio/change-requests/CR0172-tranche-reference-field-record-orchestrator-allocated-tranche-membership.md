# CR-0172: Tranche reference field: record orchestrator-allocated tranche membership in the ledger

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Priority:** Low
> **Type:** Enhancement
> **Raised-by:** Dani Okafor (Engineering amigo)
> **Depends on:** CR0167, CR0169

## Summary

An optional frontmatter field (`tranche:`) referencing the orchestrator-allocated tranche an
artefact was delivered in. sdlc-studio does not allocate or manage tranches; it records
membership so the ledger can answer "what shipped in tranche 12" and remains a complete
audit trail.

## Motivation

A decided design boundary: work allocation into tranches, claiming, and scheduling belong to
external orchestrator agents, not to sdlc-studio. sdlc-studio is the system of record - the
ledger - and must be passively safe under concurrent writes when orchestration fails, but it
is not a scheduler. Without a place to record tranche membership, the orchestrator's history
lives only in the orchestrator, and the ledger cannot answer delivery questions or support
the CR0173 triage metrics per tranche. A single optional reference field keeps the boundary
clean: the orchestrator writes it, sdlc-studio merely validates its shape and reports on it.

## Scope

**In scope**

- Optional frontmatter field `tranche:` (opaque string reference, orchestrator-defined
  format) on CRs, bugs, stories, and epics.
- `validate.py` shape check only (non-empty string when present); never required.
- `status.py` and reconcile reporting can group or filter by tranche (read-only projection:
  "what shipped in tranche 12").
- Documented in the schema reference as orchestrator-written, sdlc-studio-read.

**Out of scope (explicit, by decided boundary)**

- Any scheduling, claiming, or lease behaviour.
- Tranche allocation, naming, ordering, or lifecycle - the field is a foreign key to a
  system sdlc-studio does not own.
- Validation that a tranche "exists": sdlc-studio has no registry to check against, by
  design.

## Acceptance Criteria

- [ ] `tranche:` is accepted on CR/bug/story/epic frontmatter and absent-by-default on all
      scaffolds.
- [ ] `validate.py` passes artefacts with and without the field; fails an empty or
      non-string value.
- [ ] A status/reconcile query lists all artefacts carrying a given tranche reference
      ("what shipped in tranche 12" answered from the ledger alone; test fixture).
- [ ] No code path in sdlc-studio writes the field except pass-through flags (e.g.
      `artifact.py new --tranche` for orchestrators that create via the tool).
- [ ] Docs state the boundary verbatim: sdlc-studio records membership, never allocates it.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0167 | Blocking: orchestrators cross-reference artefacts by id at creation time, which needs collision-free identity |
| CR0169 | Blocking: lands in the same schema-v3 frontmatter pass |

## Effort

**S.** One optional field, a shape check, and a reporting filter.

## Risk

Scope creep is the only real risk: a tranche field invites "just add claiming" requests.
The out-of-scope list is written to be quoted back at those requests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Full scope drafted; ledger-not-scheduler boundary quoted |
