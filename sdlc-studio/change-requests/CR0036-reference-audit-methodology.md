# CR-0036: reference-audit.md methodology + project lens packs (RFC0002 WS1)

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Autosprint (RFC0002)
> **RFC:** RFC-0002
> **Date:** 2026-06-20
> **Affects:** reference-audit.md (new), SKILL.md, help/references.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Spawned from RFC0002 WS1. Ship the portable audit methodology as `reference-audit.md`:
the find -> verify -> merge -> file pipeline, the project + skill lens profiles (with the
D5 lens-pack table), the refute panel (N-of-M, default 3-vote >=2/3), the Bug/CR/RFC
taxonomy + filing (triage-default, via file_finding.py), and the budget controls. The
headline of RFC0002's "Option A now" - tool-neutral, no runtime dependency.

## Acceptance Criteria

- [x] `reference-audit.md` documents the four-stage pipeline, both lens profiles incl. the project lens packs, the configurable refute panel, the taxonomy + filing, and the budget controls.
- [x] It points to `file_finding.py` and the `templates/automation/audit-*.md` harness.
- [x] It is reachable from the SKILL.md Progressive Loading Guide and help/references.md.
- [x] Anchor-links + lint pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0002) | Complete - reference-audit.md + router wiring |
