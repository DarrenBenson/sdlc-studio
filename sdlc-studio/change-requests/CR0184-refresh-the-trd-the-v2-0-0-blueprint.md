# CR-0184: Refresh the TRD: the v2.0.0 blueprint misdescribes the v3.5.0 script layer, write contract and state files

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0012](../epics/EP0012-distributed-artefact-identity-schema-v3.md)
> **Priority:** Medium
> **Type:** Improvement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

The TRD - the generated rebuild blueprint - is two major versions stale (v2.0.0, 2026-06-20)
and misdescribes the script layer's size, write behaviour, and state files at project v3.5.0.

## Motivation

The TRD presents itself as "detailed enough to rebuild SDLC Studio on a different agent
harness", but anyone trusting its documented write-contract will assume scripts cannot mutate
stories, indexes, or source files - which is now false (transition, reconcile apply,
artifact, file_finding, github_sync, and mutation all write). The documented state-file
inventory and scale figures are wrong. The repo's own doctrine ("paperwork in the same
commit") is violated by its flagship generated artefact, and the review found the
write-contract drift is exactly where a reviewer's assumptions would break.

## Scope

**In scope**

- Regenerate/refresh the TRD: component counts (43 top-level scripts, not "10"; 46 reference
  and 39 help files, not 42/31), script-contract rule 5 (the real write surface:
  transition.py:237, reconcile.py:967 apply, artifact.py:285, file_finding.py:170,
  github_sync.py:310, mutation.py:196 restored-in-finally), the JSON-state table (drop the
  non-existent `.local/status-cache.json`; add telemetry/verify-history), and the test
  figures (1160 tests, not "181").
- Correct the "scripts are read-only over the workspace" claim (trd.md:424).
- Add a `doc_freshness`-style guard for TRD claims, the way LATEST.md claims are guarded, so
  this cannot silently rot again.

**Out of scope**

- Re-running full generate mode from scratch if a targeted refresh suffices.
- The reconcile module docstring fix (folded into CR0187 code-quality debt).

## Acceptance Criteria

- [ ] TRD version, component counts, script-contract write surface, state-file inventory, and
      test figures match the shipped v3.5.0 code (spot-checkable against the cited lines).
- [ ] The "read-only over the workspace" claim is corrected to the real write contract.
- [ ] A freshness guard flags a future TRD scale/contract claim that drifts from code.
- [ ] `check_versions.py` sees the TRD at the current version.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0177 | Sibling positioning/doc work (README); different document, coordinate wording |
| CR0185 | The invariant tests give the TRD's write-contract claims an executable backstop |

## Risk

Low. Documentation-only, but the freshness guard must not be so strict it blocks routine TRD
edits; scope it to the enumerated scale/contract claims.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted from RV0006 architecture leg |
