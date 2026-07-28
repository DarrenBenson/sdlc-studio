# CR-0461: An acceptance criterion can describe a function nothing calls, and nothing refuses it

> **Status:** Complete
> **Decomposed-into:** EP0178
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-decisions.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/core/story.md
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ retro, four inert mechanisms); agent; skill v5.0.0

## Summary

Four mechanisms shipped INERT in one sprint - correct, tested, and reaching no caller. The surface hash could never match because a volatile directory sat in the digest. The selection was computed by one hook and ignored by the one that runs tests. The prune-candidate consumer needs evidence no producer emits. A dead-flag detector in an earlier sprint was invoked by nothing at all. Every one had passing tests, a green gate and an author who believed it worked, and each was found only by an independent reader or by a delivery lane's friction report.

The common shape is that an acceptance criterion described a FUNCTION and never named the CALLER. A criterion of the form 'the checker reports X' is satisfied by a checker nothing runs. The retro records this as a lesson (name the caller, not only the function) and a lesson gates nothing, so the next unit is free to repeat it.

## Impact

Who: every unit that adds a mechanism, in this project and in every consuming one - which is most units. What breaks: a unit reaches Done with green evidence for a capability production cannot reach, and the artefact graph then asserts a capability the system does not have. That is the class this skill exists to prevent, arriving through the criteria rather than through the code. It is also expensive to catch late: each of the four cost a full review round and a repair cycle, and one was reported to the operator as working before it was found.

## Acceptance Criteria

- [ ] A unit that adds or changes a mechanism carries at least one acceptance criterion naming the CALLER that consumes it - the hook, the lane, the command - not only the function's own behaviour.
- [ ] A unit whose mechanism has no caller yet states that explicitly as consumer-only or producer-only, and names the follow-up that completes it, so the gap is recorded rather than implied.
- [ ] The Ready criteria and the story template say this in the place an author is looking when they write the criterion, not only in a lesson they would have to recall.
- [ ] The adversarial review prompt asks it directly - does this criterion describe a function nothing calls - so it is checked by the pass that has caught every instance so far.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ retro, four inert mechanisms) | Raised |
