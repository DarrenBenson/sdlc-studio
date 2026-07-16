# CR-0242: Recall: the cross-project registry gets an automatic reader (review, audit, plan)

> **Status:** Complete
> **Size:** M
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

- [ ] Sprint plan, review and audit each emit the still-valid cross-project lessons as one line per
      lesson, in the output the agent already reads - an agent running any of the three sees them
      without asking for them.
- [ ] The digest is the FULL still-valid set, not a tag-filtered subset: every lesson in the
      registry appears, LL0004/LL0006/LL0021 included. A filter is how a fix exempts the lesson it
      forgot (LL0013).
- [ ] The plan digest cap is raised to 50 and the elided tail still prints its `+N more` count, so
      nothing is dropped silently.
- [ ] A project with an empty project-tier store still recalls the skill-tier registry, so the
      lessons lens works on day one rather than after the first local lesson is written.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
