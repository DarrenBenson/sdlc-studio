# BG0025: project_upgrade dry-run omits the stale .version bump that --apply performs

> **Status:** Fixed
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Severity:** Medium

## Summary

A consuming project that is schema-current but whose `.version` records an older skill (e.g. 1.6.0 < installed 2.4.0): `project upgrade` (dry-run) reported AUTO findings empty ("nothing auto-correctable"), yet `--apply` bumped `.version` 1.6.0 -> 2.4.0. The dry-run under-reported what apply does - a dry-run must accurately preview apply.

## Steps to Reproduce

On a project with a present-but-stale `sdlc-studio/.version`: `project upgrade` shows no auto-correctable items; `project upgrade --apply` then updates `.version`.

## Proposed Fix

`audit()` only flagged a MISSING `.version`; add a `stale-version` auto finding when `.version` exists but its skill_version != installed (or schema < current), so the dry-run matches `apply()` (which already bumps it). Fixed + tested.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | sdlc | Created via `new` (deterministic) |
