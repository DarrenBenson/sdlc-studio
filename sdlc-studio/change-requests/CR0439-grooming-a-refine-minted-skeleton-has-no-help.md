# CR-0439: Grooming a refine-minted skeleton has no help page and no pointer to the AC shape, so each groom re-derives it

> **Status:** In Progress
> **Decomposed-into:** EP0170
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/SKILL.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (dogfooding friction, CR0425/CR0426 groom); agent; skill v5.0.0

## Summary

refine mints every multi-story breakdown with an ungroomed AC placeholder reading 'author each criterion and its Verify check against this story's slice while grooming' - which names no source. The shape it asks for is documented (templates/core/story.md carries the Given/When/Then/Verify/Verified block) and what makes a Verify line discriminating rather than vacuous is documented too (reference-verify.md, help/verify.md), but the placeholder cites neither. There is also no help/refine.md at all: refine is a first-class type in SKILL.md's Type Reference and its mirror command triage has help/triage.md, so an agent following SKILL.md's own instruction to 'read help/{type}.md' finds nothing for the command that mints most stories, and the Progressive Loading Guide has no grooming row.

## Impact

Who: every agent or operator grooming a skeleton, in this repo and in every consuming project. What breaks: the groomer re-derives the AC shape by reading an existing story (observed live in the CR0425/CR0426 groom on 2026-07-27 - avoidable tokens spent inferring a shape the template already ships), and, worse, authors a Verify line with no guidance on what makes one able to fail. That is the upstream cause of the vacuous-selector class the 2026-07-27 audit kept finding (US0444's grep-for-a-phrase, CR0433's non-discriminating shared selectors): the instruction to write a Verify check is given at exactly the moment the guidance on writing a good one is not.

## Acceptance Criteria

- [ ] The ungroomed AC placeholder refine writes names where the shape and the verifier guidance live - the story template and the verify reference - so a groomer is routed rather than left to infer.
- [ ] help/refine.md ships, covering the decompose-then-groom flow (propose a breakdown, apply, groom the skeletons, transition to Ready), mirroring help/triage.md which already exists for the sibling command.
- [ ] SKILL.md's Progressive Loading Guide carries a grooming row pointing at the story template and reference-verify.md, so the route is discoverable from the always-loaded router rather than only from the placeholder.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (dogfooding friction, CR0425/CR0426 groom) | Raised |
