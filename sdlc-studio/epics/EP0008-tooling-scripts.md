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
indexing, GitHub sync, ID allocation, validation, review prep, and schema
upgrade. Pure stdlib, read-only over the workspace, unit-tested.

**PRD Reference:** [Tech Stack](../prd.md#1-project-overview)

## Scope

### In Scope

- `repo_map.py` - AST repo indexer, ranks files for a story.
- `github_sync.py` - two-way Issues sync via `gh`.
- `next_id.py` - deterministic, cross-repo-aware ID allocation.
- `validate.py` - skill + instructions hygiene checks.
- `review_prep.py` - review preparation data.
- Schema upgrade (`reference-upgrade.md`).

### Out of Scope

- reconcile/verify_ac/status scripts (owned by EP0005, the quality plane).

### Affected Personas

- **AI Agent:** invokes scripts via `$CLAUDE_SKILL_DIR`.
- **Skill Maintainer:** keeps scripts tested before release.

## Acceptance Criteria (Epic Level)

- [ ] Each script is pure stdlib (Python 3.10+) and needs no third-party packages.
- [ ] Scripts emitting data return machine-readable JSON.
- [ ] `next_id` prevents collisions and checks `origin/main` with `--remote`.
- [ ] `repo_map build` produces `.local/repo-map.json` without ctags/tree-sitter.
- [ ] All scripts covered by `scripts/tests/` (181 passing at extraction).

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| None | -- | -- | -- |

## Sizing

**Estimated Story Count:** 6

## Story Breakdown

- [ ] US: Repo map indexer + file ranking
- [ ] US: GitHub Issues two-way sync
- [ ] US: Deterministic next-ID allocation (cross-repo)
- [ ] US: Skill + instructions validation
- [ ] US: Review prep data helper
- [ ] US: Schema upgrade between versions

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
