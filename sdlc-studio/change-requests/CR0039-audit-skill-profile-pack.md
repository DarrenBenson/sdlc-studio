# CR-0039: package the skill-profile lens pack (RFC0002 WS5)

> **Status:** Complete
> **Priority:** Low
> **Type:** Feature
> **Requester:** Autosprint (RFC0002)
> **RFC:** RFC-0002
> **Date:** 2026-06-20
> **Affects:** templates/audit-profiles/skill.md (new), reference-audit.md
> **Depends on:** CR0036 (WS1)
> **GitHub Issue:** --

## Summary

Spawned from RFC0002 WS5, unblocked once WS1 (reference-audit.md) shipped. Package the
four skill-audit lenses (over-engineering, token-economy, determinism,
external-benchmark) as a declared, loadable profile pack so the harness can run the
skill profile directly, and point to it from reference-audit.md.

## Proposed Changes

- New `templates/audit-profiles/skill.md`: the four lenses as a table (lens +
  adversarial question + what it hunts), usable as the `{{lens}}` of `audit-finder.md`.
- `reference-audit.md#audit-skill-profile`: point to the packaged pack.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| templates/audit-profiles/skill.md | the skill lens pack | New |
| reference-audit.md | reference the pack | Modified |

### Breaking Changes

None.

## Acceptance Criteria

- [x] `templates/audit-profiles/skill.md` declares the four skill lenses with their adversarial questions, loadable as finder lenses.
- [x] `reference-audit.md` points to the packaged pack.
- [x] Lint passes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0002) | Complete - skill-profile pack packaged |
