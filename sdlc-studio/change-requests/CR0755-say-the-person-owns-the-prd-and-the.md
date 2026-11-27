# CR-0755: Say the person owns the PRD and the PVD, and the seat holds delegated authority to check the work meets them

> **Status:** Complete
> **Decomposed-into:** EP0384
> **Priority:** Medium
> **Type:** Feature
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-prd.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-pvd.md
> **Date:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** orchestrator; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T23:54:29Z

## Summary

The operator's direction, 2026-11-25, verbatim: "Ultimately the human owns everything but the Personas have delegated authority to make changes as needed - asking if unsure." The skill says a seat owns a requirements document: reference-prd.md:201 ("The PRD is owned by the Product Owner seat"), reference-workflow-personas.md's Document-owner seats table (lines 117-129, its column headed Owns naming the Product Owner and Product Manager seats), reference-review.md:153 ("The Product Owner seat owns this") and reference-pvd.md:17-19 (the PVD owned by the Product Manager persona, the PRD by the Product Owner). The wording came in with CR0065. The website (in the website's own repository, its CR-01M8AECF) and the explainer video say the person in each role owns and edits each document and the AI seat reviews work against it, while the site's Three Amigos page mirrors the skill, so a reader finds two owners for one document. Both sides already agree the person writes the document and the seat reviews against it; they differ on the word owns. Change the wording: the person owns every document; the Product Owner (or Product Manager) seat is accountable, with delegated authority, for checking the work satisfies it, signs its review leg, and asks the person when unsure. Keep the rule that a seat never authors a document it reviews against: it proposes a change, as a CR, and the person makes it.

## Impact

The website cannot say who owns the PRD without contradicting either the skill or its own explainer until the skill's wording changes and ships in a release.

## Acceptance Criteria

- [ ] Given the skill's reference files, then no seat is said to own the PRD or the PVD: the person owns each, and the seat is accountable, with delegated authority, for checking the work satisfies it and signs its review leg. Fails on: "owned by the Product Owner seat", "The Product Owner seat owns this", or a table column headed Owns that names a seat.
  - **Verify:** shell ! grep -rniE "owned by the product owner|product owner seat owns|stays owned by the product owner" .claude/skills/sdlc-studio/reference-prd.md .claude/skills/sdlc-studio/reference-workflow-personas.md .claude/skills/sdlc-studio/reference-review.md .claude/skills/sdlc-studio/reference-pvd.md
- [ ] Given the same files, then a seat still never authors a document it reviews against: it proposes a change and the person makes it. Fails on: a seat said to edit the PRD or PVD whose review leg it signs.
  - **Verify:** manual: read the four files' ownership passages against the second criterion

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | orchestrator | Raised |
| 2026-11-26 | orchestrator | The website's repository is named generically (the neutrality lane blocklists its name) |
