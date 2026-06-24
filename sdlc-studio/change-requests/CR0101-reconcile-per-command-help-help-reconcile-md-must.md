# CR-0101: reconcile per-command help (help/reconcile.md) must point at the deterministic scripts/reconcile.py

> **Status:** Complete
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

help/reconcile.md describes the full index/count/status reconciliation as freehand model work with no pointer to scripts/reconcile.py - the one in-scope reconcile doc that omits the script, so a model loading only it may hand-recompute counts and hand-edit index rows (the recorded count-block corruption mode).

## Acceptance Criteria

- [x] help/reconcile.md 'What It Does' / 'Apply mode' name scripts/reconcile.py as the actor, mirroring reference-reconcile.md and help/status.md
- [x] The help documents the detect/apply subcommands + --dry-run flag so the model invokes the script rather than recomputing counts by hand
- [x] A 'do not hand-recompute counts or hand-edit index rows' caution is present
- [x] The See Also REQUIRED block lists scripts/reconcile.py; CHANGELOG entry same commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
