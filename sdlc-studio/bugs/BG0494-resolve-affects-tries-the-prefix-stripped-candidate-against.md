# BG0494: resolve_affects tries the prefix-stripped candidate against the repo root first, so a consuming project's own file wins

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Severity:** Medium
> **Points:** 2

## Summary

BG0436 added a skill-relative fallback to `resolve_affects` (lib/`sdlc_md.py`:2925-2950), but the loop is `for base ... for cand_rel ...`, so the prefix-stripped candidate is tried against the REPO ROOT before the skill bases.

In a project holding its own `templates/core/story.md`, `resolve_affects(root, ".claude/skills/sdlc-studio/templates/core/story.md")` therefore returns the PROJECT's file rather than the skill's. New at this commit - at 4e7d5e6c the stripped candidate did not exist, so nothing resolved. Invisible in this repo because the vendored copy wins either way, which is why it shipped.

## Steps to Reproduce

1. Create a project with its own `templates/core/story.md`.
2. Call `resolve_affects(root, '.claude/skills/sdlc-studio/templates/core/story.md')`.
3. It returns the project's file, not the skill's.

## Proposed Fix

Swap the loop nesting, or restrict the prefix-stripped candidate to the skill bases only - it is a skill-relative spelling and has no business matching at the project root.

## Impact

A consuming project that happens to hold a same-named path silently shadows the skill's copy in every Affects resolution. This repo cannot see it, which makes it exactly the kind of defect that reaches consumers first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
