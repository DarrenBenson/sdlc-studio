# CR-0459: validate does not refuse a bug reaching Fixed with no acceptance criteria, so six shipped without any

> **Status:** In Progress
> **Decomposed-into:** EP0178
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ closing review); agent; skill v5.0.0

## Summary

The project's non-negotiable is that work becomes a story or a bug with acceptance criteria before it becomes a diff. A story is held to that at Done; a bug is not held to it at Fixed. Six bugs in RUN-01KYJZGZ reached Fixed carrying no acceptance-criteria section and no verifier at all, and four carried no delivery row either, while real code landed against each. validate reports no error and conformance is story-scoped, so nothing in the machinery notices.

## Impact

Who: every project relying on the artefact graph to speak for its code. What breaks: with no criterion and no verifier, the Done-freshness spine, `verify_ac`, the release lane's unspecified-AC refusal and the close reconcile can never speak for those units - the tests exist and are good, but no artefact points at them, so a later regression is invisible to every gate that reads artefacts. It also makes such a unit unresumable: a lane picking one up cannot tell delivered from untouched.

## Acceptance Criteria

- [ ] A bug reaching a terminal status with no acceptance-criteria section is refused, as a story reaching Done already is.
- [ ] The existing instances are recorded as a baseline so the new rule blocks a new one without blocking on the backlog it reveals.
- [ ] The conformance sweep covers bugs for this stage rather than being story-scoped, so the two gates agree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ closing review) | Raised |
