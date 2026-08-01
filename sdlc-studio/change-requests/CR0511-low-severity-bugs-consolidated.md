# CR-0511: Low-severity bugs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-31
> **Consolidation:** low-severity-bugs
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Points:** 3
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **A repo-root file cannot be declared in Affects without a leading ./ and nothing says so**: `affects_files` does not read a bare root-level filename as a path, so `Affects: package-lock.json` parses to nothing and the grooming gate refuses the filing as UNGROOMED. `./package-lock.json` works. The refusal text explains that a prose phrase or bare word counts as no Affects at all, but never says that a legitimate repo-root file needs the `./`, so the author is told what is wrong without being told what to type.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Consolidation opened |
