# CR-0242: Recall: the cross-project registry gets an automatic reader (review, audit, plan)

> **Status:** Complete
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 D2, D3, D4
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P1
> **Type:** feature

## Summary

The LL registry has no automatic reader. `plan_digest` sources the project tier, not the LL registry, so LL0001-LL0022 are reachable only by explicitly running 'lessons recall' - prose doctrine, and doctrine gets skipped. Inject the full registry as one-liners (~930 tokens) at every read point: sprint plan, review and audit. Bodies are pulled on demand, never injected wholesale. Raise `PLAN_DIGEST_MAX` 20 -> 50; the elided tail stays loud. A consuming project inherits the skill-tier registry as its day-one lens (D4).

## Impact

Every review, audit and sprint plan in every project. Adds roughly 930 tokens of lessons to outputs the agent already reads. Nothing breaks; today the cross-project registry is simply never read, so LL0008 could be written down through three separate incidents and still not reach the agent about to cause the fourth.

**Effort:** M

## Acceptance Criteria

- [ ] Sprint plan, review and audit each emit the still-valid cross-project lessons as one line per lesson, in the output the agent already reads. Verify: rg -q 'lessons' .claude/skills/sdlc-studio/scripts/review.py
- [ ] The digest is the FULL set, not a tag-filtered subset - a filter would exempt LL0004/LL0006/LL0021 (LL0013).
      Verify: `python3 .claude/skills/sdlc-studio/scripts/lessons.py recall --format json | jq -e '.matches | length >= 22'`
- [ ] The plan digest cap is raised to 50 and the elided tail still prints its `+N more` count, so
      nothing is dropped silently.
- [ ] A project with an empty project-tier store still recalls the skill-tier registry (day-one lens). Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k lessons

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
