# CR-0008: Collapse three-way config-defaults duplication and make one source authoritative that scripts actually read

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** templates/config-defaults.yaml
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Every config default is written three times (config-defaults.yaml, an embedded YAML block in reference-config.md, and a prose table in reference-config.md) and no script reads the YAML, so the values drift on every edit and the only ones honoured at runtime are whatever the LLM reads from markdown.

## Problem

Each default (coverage unit 90 / integration 85 / e2e 100, story max_points 13, max_ac 10, edge_case_threshold 5, e2e max_tests_per_spec 50, persona staleness_days 90, etc.) is written in templates/config-defaults.yaml, again as a fenced YAML block in reference-config.md, and a third time as a prose table row in reference-config.md. grep for config-defaults / .config.yaml / config_defaults across scripts/ returns nothing, so config-defaults.yaml is never the runtime source of truth - the LLM reads the markdown. The three copies can and will drift on every edit.

## Proposed Changes

### Item 1: Collapse three-way config-defaults duplication and make one source authoritative that scripts actually read

**Priority:** Medium **Effort:** TBD

Pick one source of truth. Make config-defaults.yaml authoritative and have status.py / validate.py load it (they already read artifacts deterministically). In reference-config.md, delete the duplicate YAML blocks and keep only the prose tables that add the 'Used In' / 'When to Adjust' columns the YAML cannot carry, OR keep the YAML and drop the per-key value column from the tables. Do not maintain the same number in three files.

## Impact Assessment

### Existing Functionality

Three-way drift risk on every config edit; config-defaults.yaml is dead weight that looks authoritative while the runtime honours whichever of the two reference-config.md copies the LLM happens to read. Quality risk medium.

## Acceptance Criteria

- [x] `config-defaults.yaml` is the single source of truth and `status.py` / `validate.py` load a representative default from it rather than a hard-coded literal.
- [x] The duplicate YAML block in `reference-config.md` is removed (the value lives in one place, not three); a test asserts the default resolves from the YAML.

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (determinism-sprint) | Complete - config.py loader (status.py reads it), 12 doc fences removed, drift-guard test; critic REJECT (AC1 integration + staleness drift) repaired |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: over-engineering; evidence: templates/config-defaults.yaml:11-13 (unit:90/integration:85/e2e:100) duplicated at reference-config.md:53 (YAML) and :60 (prose table); grep for config-defaults/.config.yaml/config_defaults across scripts/*.py returns no hits) |
