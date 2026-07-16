# CR-0297: validate's persona gate checks only the personas/ registry and gives a silent clean pass to the personas.md-only layout the story pipeline hard-gates on

> **Status:** Complete
> **Decomposed-into:** EP0051
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

`check_personas` (validate.py:491-565) scans only sdlc-studio/personas/*.md and no-ops (then prints 'personas look well-formed.') when the directory is absent; validate.py contains zero references to personas.md. Meanwhile reference-story.md hard-gates story creation on personas.md and reads persona attributes from it - so the file the story pipeline actually consumes gets zero structural validation (an empty-boilerplate personas.md passes validate clean), while the painstakingly-checked personas/ cards are not what the story workflow reads. The docstring even applies LL0008 to the nested-subdir case ('emit an advisory rather than a clean pass on an empty inspection') while giving exactly that clean pass to the personas.md-only layout. Panel split 2-1: the refuter noted personas.md is a supported legacy layout with a different schema - so the fix is an advisory/lighter structural check, not the full template check. Companion to the reference-story rewiring CR; still worthwhile independently.

## Impact

`check_personas` (validate.py:491-565) scans only sdlc-studio/personas/*.md and no-ops (then prints 'personas look well-formed.') when the directory is absent; validate.py contains zero references to personas.md.

## Acceptance Criteria

- [x] validate personas on a personas.md-only project emits at least a layout advisory (legacy flat file in use; personas/ registry absent) instead of a vacuous clean pass
- [x] An empty or template-boilerplate personas.md is flagged
- [x] The docstring's LL0008 rationale covers this layout explicitly

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
