# CR-0283: Story workflows read only the legacy personas.md; the Cooper design registry (personas/) with the declared Primary is unreachable from story generation

> **Status:** Complete
> **Decomposed-into:** EP0049
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-story.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Both story workflows (create and generate) in reference-story.md gate on and read personas exclusively from the legacy flat sdlc-studio/personas.md ('Check sdlc-studio/personas.md exists - If missing: create from template, ask user to populate, STOP'; 'Read personas (name, role, goals, pain points)'). The file contains zero references to sdlc-studio/personas/, yet current persona doctrine writes design personas there (reference-persona.md: 'Write to sdlc-studio/personas/[name].md'; reference-persona-generate.md: personas/[category]/). A project that followed the skill's own persona commands has no personas.md, so story generation STOPs on a legacy file, and the declared Primary (personas/index.md: 'the design target') can never influence step 3a's persona selection. This is the structural cause of design personas being non-load-bearing: the workflow that assigns a story's persona is wired to the registry that does not contain them. BG0004 fixed the same reader/writer split for `review_prep.py` only; RFC0017 left the migration open. Verified 3x.

## Impact

Both story workflows (create and generate) in reference-story.md gate on and read personas exclusively from the legacy flat sdlc-studio/personas.md ('Check sdlc-studio/personas.md exists - If missing: create from template, ask user to populate, STOP'; 'Read personas (name, role, goals, pain points)').

## Acceptance Criteria

- [x] Story create and generate prerequisites resolve personas from the personas/ registry (index.md and per-persona cards) with personas.md as a documented legacy fallback
- [x] A project using only the personas/ layout is not STOPped or told to populate personas.md
- [x] Step 3a's 'select most relevant persona' reads the declared Primary from personas/index.md
- [x] Help files and reference-story.md agree on where personas live

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
