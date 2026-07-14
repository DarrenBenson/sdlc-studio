# BG0127: Several _index.md writers bypass atomic_write, the module's own torn-write guard

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/archive.py

## Summary

`sdlc_md.atomic_write` exists so a reader never sees a half-written index, and it is used on the main paths. But four index-mutating paths write the live _index.md with plain `Path.write_text`: reconcile.py:1405 (`project_fields` rewrites the whole story index), reconcile.py:1615-1616 (`archive_type)`, artifact.py:558 (`meta_new` row insert), archive.py:109 (trims the live index while using `atomic_write` for the archive file two lines up). A crash or concurrent read mid-write leaves a corrupt registry - the exact hazard `atomic_write` was written to prevent, applied inconsistently within the same modules (LL0008).

## Steps to Reproduce

grep -n '`write_text`' reconcile.py artifact.py archive.py and compare against `atomic_write` usage. archive.py uses `atomic_write` at :88/:90 for the archive file but plain `write_text` at :109 for the live index.

## Proposed Fix

Route all _index.md writes through `sdlc_md.atomic_write.`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
