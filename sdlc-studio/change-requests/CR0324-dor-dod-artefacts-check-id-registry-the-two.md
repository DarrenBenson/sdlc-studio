# CR-0324: DoR/DoD artefacts + check-id registry: the two editable documents with a tagged machine-checkable subset (RFC0043 slice 1)

> **Status:** Proposed
> **Parent:** RFC0043
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/templates/core/definition-of-ready.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-decisions.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; RFC triage decisions, filed by Claude Fable 5

## Summary

RFC0043 slice 1 (D1 hybrid + D2 check-id registry, operator-decided): ship editable definition-of-ready.md and definition-of-done.md templates (multi-level: story/sprint/release) whose criteria are checklist items; an enforceable criterion carries a [check: <id>] tag resolving through a registered check-id vocabulary (grooming.affects, grooming.points, story.verify-ac, review.critic-approve, close.retro, release.gate...). One registry, gates refuse an unknown id loudly; untagged criteria are explicitly human-judged. The documents are the single source: human intent and enforced rule cannot drift apart.

## Impact

The quality bar lives scattered and unnamed across grooming, `verify_ac`, the critic and the close gate; a project cannot see, edit or strengthen its own definition of ready/done as one artefact.

## Acceptance Criteria

- [ ] The two templates ship with default criteria per level, each enforceable one tagged with a registered check id; the registry lives in one authority module
- [ ] An unknown check id in either document is a loud validation error, never silently unenforced
- [ ] Documentation states the non-negotiable rule: under pressure cut scope, never weaken the bar

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
