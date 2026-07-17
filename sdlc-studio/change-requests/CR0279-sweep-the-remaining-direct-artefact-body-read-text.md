# CR-0279: Sweep the remaining direct artefact-body read_text calls through read_text_safe

> **Status:** In Progress
> **Decomposed-into:** EP0082
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The RFC0037 review hardened `iter_artifact_files`, `reconcile.file_census` and `close_owed` against a non-UTF-8 artefact; retro.py had one more (fixed inline this sprint). A project-wide sweep is owed: other scripts likely read an artefact body via a bare `read_text` and would crash a scanner on a corrupt file. Mechanical - route artefact-body reads through the shared `sdlc_md.read_text_safe`, leaving index-file reads loud.

## Impact

A non-UTF-8 artefact from a crashed session crashes any scanner reading its body via a bare `read_text.` Low severity (needs a corrupt file) but the fix is mechanical and the pattern recurs.

## Acceptance Criteria

- [ ] route each artefact-body `read_text(encoding`=utf-8) through `read_text_safe` (index-file reads stay loud)
- [ ] a regression test drives a representative scanner with a non-UTF-8 artefact and asserts no crash

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Raised |
