# US0723: A verdict records the base commit the review was measured against

> **Status:** Won't Implement
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Delivers:** CR0509
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0225
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A verdict records the base commit the review was measured against
**So that** CR0509 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its Verify check against this story's slice while grooming, before it is planned to Done. Shape: `templates/core/story.md`. Verifier guidance: `reference-verify.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - the review base recorded today is the unit's verdict row count, not a commit (critic._mark_review_base), so the planning reason was wrong; US0722 (kept) stops a review on a tree without the unit before it runs, which is the defect this epic exists for, so a commit stamped on each verdict afterwards adds a field no persona reads |
