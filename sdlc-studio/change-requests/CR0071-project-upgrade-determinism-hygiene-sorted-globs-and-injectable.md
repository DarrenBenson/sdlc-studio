# CR-0071: project_upgrade determinism hygiene sorted globs and injectable date (review WS B1)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

Determinism/testability hygiene flagged by the world-class audit (the determinism lens). `project_upgrade` wrote `.version` dates via a non-injectable `date.today()` (untestable) and scanned `personas/` with an unsorted glob. No live bug (the glob returns a bool any-match), but a deterministic date + reproducible scan are cheap hardening.

## Acceptance Criteria

- [x] `_bump_version_text` + `apply` take an injectable `today` (default `date.today()`); tests pin a fixed date on both the bump and create paths
- [x] `_old_persona_model` scans `sorted(glob(...))` for filesystem-independent, reproducible behaviour
- [x] gate green; no behaviour change for real runs

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
