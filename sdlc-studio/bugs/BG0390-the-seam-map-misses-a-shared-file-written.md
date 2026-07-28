# BG0390: The seam map misses a shared file written in the two Affects spellings this repo accepts

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`sdlc_md.resolve_affects` deliberately resolves both repo-relative and skill-relative paths and the corpus uses both (149 `.claude/skills/sdlc-studio/scripts/sprint.py` against 1 `scripts/sprint.py`). `seam_map` intersects raw strings, so the same file under two spellings is not a seam.

## Steps to Reproduce

US0001 Affects .claude/skills/sdlc-studio/scripts/critic.py; US0002 Affects scripts/critic.py -> `seam_map` returns [].

## Proposed Fix

Normalise through `sdlc_md.resolve_affects` before intersecting.

## Acceptance Criteria

- [ ] Two units naming one file in different accepted spellings are a seam.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
