# CR-0249: Derive per-type status vocab from the single source instead of triplicating it

> **Status:** Complete
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/file_finding.py

## Summary

`sdlc_md.STATUS_VOCAB`/`TERMINAL_STATUS` is the stated single source, but artifact.SPEC (artifact.py:29-38) and `file_finding.TYPES` (`file_finding.py`:33-43) each re-hardcode per-type statuses. They agree today, but a vocab change must be made in three places or they drift; close() defaults its terminal status from artifact.SPEC, not from `sdlc_md.TERMINAL_STATUS.` Maintainability, not a live bug.

## Impact

Every future status-vocab change risks silent drift between the three hardcoded copies; the single-source-of-truth claim is only partly true.

**Effort:** S

## Acceptance Criteria

- [ ] SPEC/TYPES status defaults derive from `sdlc_md` rather than restating them. Verify: rg -n '`terminal_statuses`|`STATUS_VOCAB`' artifact.py `file_finding.py` finds the derivation

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
