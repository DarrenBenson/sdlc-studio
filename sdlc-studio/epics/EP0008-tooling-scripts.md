# EP0008: Tooling & Scripts

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

The deterministic Python layer that side-effecting and analytical work is
delegated to, so the agent reasons over JSON rather than parsing markdown: repo
indexing, GitHub sync, ID allocation, validation, and schema upgrade. Pure
stdlib, read-only over the workspace, unit-tested.

**PRD Reference:** [Tech Stack](../prd.md#1-project-overview)

## Scope

### In Scope

- `repo_map.py` - AST repo indexer, ranks files for a story.
- `github_sync.py` - two-way Issues sync via `gh`.
- `next_id.py` - deterministic, cross-repo-aware ID allocation.
- `validate.py` - skill + instructions hygiene checks.
- Schema upgrade (`reference-upgrade.md`).

### Out of Scope

- reconcile/verify_ac/review_prep/status scripts (owned by EP0005, the quality plane).

### Affected Personas

- **AI Agent:** invokes scripts via `$CLAUDE_SKILL_DIR`.
- **Skill Maintainer:** keeps scripts tested before release.

## Acceptance Criteria (Epic Level)

- [ ] Each script is pure stdlib (Python 3.10+) and needs no third-party packages.
- [ ] Scripts emitting data return machine-readable JSON.
- [ ] `next_id` prevents collisions and checks `origin/main` with `--remote`.
- [ ] `repo_map build` produces `.local/repo-map.json` without ctags/tree-sitter.
- [ ] Every script under `scripts/` has unit tests and the suite passes (`npm test` exits 0; 181 at extraction 2026-06-20).

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| None | -- | -- | -- |

## Sizing

**Estimated Story Count:** 5

## Story Breakdown

- [ ] US: Repo map indexer + file ranking
- [ ] US: GitHub Issues two-way sync
- [ ] [US0005: Deterministic next-ID allocation (cross-repo)](../stories/US0005-next-id-allocation.md)
- [ ] US: Skill + instructions validation
- [ ] US: Schema upgrade between versions
- [x] [US0015: Config single source](../stories/US0015-config-single-source.md) (CR0008, determinism sprint)
- [x] [US0024: config-extensible status vocabulary](../stories/US0024-config-extensible-status-vocab.md) (CR0027, consuming repo A)
- [x] [US0030: skill version check + self-update signal](../stories/US0030-skill-version-check.md) (CR0044)
- [x] [US0031: portable CI quality gate](../stories/US0031-portable-ci-gate.md) (CR0046)
- [x] [US0032: PVD template + product manifest](../stories/US0032-pvd-template-and-manifest.md) (CR0047)
- [x] [US0033: read-only PVD projection + drift check](../stories/US0033-pvd-projection-drift.md) (CR0048)
- [x] [US0034: product reconcile - cross-repo feature-map traceability](../stories/US0034-product-reconcile-traceability.md) (CR0049)
- [x] [US0026: complexity computation (cognitive + cyclomatic)](../stories/US0026-complexity-computation.md) (CR0028, RFC0009 WS1)
- [x] [US0027: code plan complexity estimation + refactor-first](../stories/US0027-code-plan-complexity-estimation.md) (CR0029, RFC0009 WS2)
- [x] [US0035: deterministic artifact create and close cascade](../stories/US0035-deterministic-artifact-create-and-close-cascade.md)
- [x] [US0036: telemetry recorder and local jsonl schema](../stories/US0036-telemetry-recorder-and-local-jsonl-schema.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
