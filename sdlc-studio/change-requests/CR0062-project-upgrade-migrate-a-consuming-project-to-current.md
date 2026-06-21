# CR-0062: project upgrade migrate a consuming project to current conventions offered by skill-update

> **Status:** Complete
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

Existing users who load a newer skill have a project on stale conventions; `skill-update` updates
the tool but never the project. Add `/sdlc-studio project upgrade` (`scripts/project_upgrade.py`):
detect the version/convention gap, audit the project, and migrate it - **dry-run by default**,
`--apply` for the safe deterministic set, a **report** for the judgement items (no CRs filed).
skill-update offers it after a version bump. Reuses reconcile/validate/next_id/version_check.

## Acceptance Criteria

- [x] `project_upgrade.py` detects the gap (project `.version` vs installed skill), no-ops when current
- [x] dry-run report splits findings into auto-correctable vs needs-judgement; `--apply` performs only
  the safe set (scaffold `.config.yaml` with `provenance.adopt_after` cutoff, scaffold/bump `.version`,
  reconcile drift); idempotent; nothing destructive; never files CRs
- [x] detects the old (pre-RFC0017) persona model incl. the nested two-category structure
- [x] `reference-upgrade.md` orchestration + `reference-skill-update.md` offer + help + reference-scripts entry
- [x] tested; validated read-only against a real consuming project (engram-studio) - report matches the recon

## Implementation

New `scripts/project_upgrade.py` (`detect`/`audit`/`apply`, dry-run default) + tests. Docs:
`reference-upgrade.md#project-upgrade-workflow`, `reference-skill-update.md` offer, `help/upgrade.md`,
`help/help.md`, `reference-scripts.md`. Dogfood: `--apply` on this repo bumped its own stale
`.version` (2.0.0 -> 2.3.0). Reuses existing fixers - no migration engine.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint | Created via `new` (deterministic) |
