# CR-0341: Close review-current: distinguish a freshly-written-but-uncommitted LATEST.md from a stale one

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The close gate's review-current lane reads LATEST.md's COMMITTED git time (`review_prep._modified_iso)`, so a just-written review that is not yet committed reads at its OLD commit time and the lane reports every artefact as stale (at the RUN-01KXQH64 close: '71 artefacts changed since the last review'). The fix - commit the review + retro paperwork, then re-run close - is not obvious from the message, which says 'run review'. The write-review then run-close then commit then re-close loop is awkward.

## Impact

An operator/agent writing the review inline and then closing hits a confusing false-stale failure that points at 'run review' rather than 'commit the review you just wrote'; wastes a diagnosis cycle every close.

## Acceptance Criteria

- [ ] When LATEST.md is MODIFIED in the working tree relative to HEAD, review-current either treats it as pending-current (with a 'commit it to make the review durable' note) OR fails with a message that names the real fix - 'reviews/LATEST.md is written but uncommitted; commit it, then close' - not a generic 'run review'.
- [ ] Alternatively (or additionally): the sprint close command commits the review/retro/lessons paperwork itself before running the close gate, so the ordering is not a manual dance.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
