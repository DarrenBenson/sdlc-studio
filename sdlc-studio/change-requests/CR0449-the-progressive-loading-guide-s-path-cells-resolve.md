# CR-0449: The Progressive Loading Guide's path cells resolve

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/../SKILL.md, tools/check_links.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (scope residue from the D0069 cap); agent; skill v5.0.0

## Summary

Cut from US0466 as scope CR0439 did not ask for. Roughly a third of the guide's cells are not resolvable paths - templated forms like help/{type}.md, script invocations, section anchors - so a naive resolver over the always-loaded router would fail on its own content.

## Impact

Who: an agent following the router to a file that is not there. What breaks: the always-loaded entry point can point at nothing and no guard notices.

## Acceptance Criteria

- [ ] Every cell the guide presents as a path resolves, with templated and anchor forms classified rather than treated as broken.
- [ ] The classification is derived from the cell's own shape, so a new templated form is not silently reported as a broken link.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (scope residue from the D0069 cap) | Raised |
