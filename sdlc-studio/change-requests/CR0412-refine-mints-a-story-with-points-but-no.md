# CR-0412: refine mints a story with points but no Affects and placeholder acceptance criteria, so a refined backlog is unplannable until a separate grooming pass - refine should make its output actionable

> **Status:** In Progress
> **Decomposed-into:** EP0155
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py,.claude/skills/sdlc-studio/reference-rfc.md,.claude/skills/sdlc-studio/reference-cr.md
> **Date:** 2026-07-23
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator observation planning the three-sprint run, filed by Claude Opus 4.8

## Summary

Hit live planning Sprint 1 of a three-sprint run over the freshly-refined discovery backlog. `refine apply --story 'title|points'` mints a story with a Points value but NO Affects and a `{{placeholder}}` acceptance-criteria block. The Affects arg is OPTIONAL (`title|points|affects`), and in practice a bulk refine over dozens of requests supplies only title and points, because the parent CR's Affects is a list the caller would have to split across the stories by hand. The result: `sprint plan` REFUSES the whole batch as ungroomed (`lacks: Affects`), so a backlog that reads as 65 sized stories and 182 points cannot be planned at all until a separate grooming pass authors Affects and real ACs on every one. The two-backlog model treats a refined request as DELIVERY work - sized, ready to sprint - but the artefact refine produces is not deliverable; it is a design-rung input. That gap is the META-LESSON from the 2026-07-17 backlog refinement ('bulk-refining the whole backlog at once outran the tooling') made concrete: the enabling feature that was supposed to close it is refine itself, and refine still stops one step short of an actionable unit.

The honest framing: a story with points but no Affects is a false promise of readiness. Points say 'this is sized delivery work'; the absent Affects says 'nobody can plan it, size it for collisions, or read it in the engagement floor'. The two contradict on the same artefact, exactly the shape US0326/BG0257-class guards refuse elsewhere.

## Impact

Every project that refines a request into stories, and worst at scale: this repo just refined 39 CRs into 65 stories and 182 points that LOOK like a ready delivery backlog and are in fact 65 grooming tasks. An operator planning from that backlog hits a full-batch refusal and has to groom before they can even see a plan. The cost compounds across the three planned sprints - each 60-point batch needs a grooming pass the points do not account for, so the velocity row understates every sprint's true cost.

## Acceptance Criteria

- [ ] refine REQUIRES an Affects per story (or a per-story way to inherit and narrow the parent request's Affects), so a minted story is plannable the moment it exists - `sprint plan` does not refuse it as ungroomed.
- [ ] Where the caller supplies no Affects, refine either refuses with a message naming what to add (the grooming-refusal idiom), or seeds a defensible Affects from the parent request and marks it for confirmation - it does NOT silently mint an unplannable unit.
- [ ] The acceptance-criteria block a refined story carries is honestly labelled as a grooming placeholder, not left as `{{placeholder}}` that reads as content - so a reader can tell a groomed story from an ungroomed one at a glance, and the count of ungroomed units is machine-visible.
- [ ] reference-cr.md / reference-rfc.md state that refine produces a PLANNABLE unit (Affects present) whose ACs still need grooming, so the two-backlog promise - a refined request is delivery work - is true rather than aspirational.
- [ ] The behaviour is chosen deliberately per project: a project that wants the old lenient behaviour can opt out, but the default makes refine output actionable.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | Darren Benson | Raised |
