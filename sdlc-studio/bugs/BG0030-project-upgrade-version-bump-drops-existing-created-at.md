# BG0030: project upgrade version bump drops existing created_at field

> **Status:** Fixed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** Medium

## Summary

The `.version` bump rewrote the file from a template, dropping any author fields (e.g. `created_at`). The a consuming project operator hand-edited to avoid the loss.

## Steps to Reproduce

`project upgrade --apply` on a project whose `.version` has a `created_at` -> the field is gone after the bump.

## Proposed Fix

Bumping an existing `.version` is now a surgical field update (`_bump_version_text`) that sets schema/skill + upgraded_from/at and preserves every other line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
