# CR-0248: Consolidate the two divergent archive writers into one

> **Status:** Complete
> **Priority:** P2
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/archive.py, .claude/skills/sdlc-studio/scripts/reconcile.py

## Summary

archive.py::archive and reconcile.py::`archive_type` are both CLI-reachable 'archive' subcommands that relocate a type's terminal index rows, but their WRITE sides disagree on layout: archive.py writes <type>/archive/{release}/{type}.md (per-release) and stamps a live-index pointer; `reconcile.archive_type` writes <type>/archive/_index.md (single file, no release grouping) with no pointer. Archiving one release with archive.py then running reconcile archive splits a type's terminal rows across two incompatible schemes; census survives (both rglob the archive dir) so nothing flags the incoherence - silent (LL0016). `reconcile.archive_type` is also undocumented in reference-scripts.md.

## Impact

An operator who uses both entry points gets a silently incoherent archive layout and a live index with a pointer for one scheme but not the other. No data loss, but the archive becomes untrustworthy and reconcile cannot detect it.

**Effort:** M

## Acceptance Criteria

- [ ] One archive layout and one writer: reconcile delegates to archive.py::archive (or vice-versa); the duplicate `archive_type`/`archive_plan`/`cmd_archive` path is removed. Verify: rg -c '`add_parser..archive`' reconcile.py returns 0

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
