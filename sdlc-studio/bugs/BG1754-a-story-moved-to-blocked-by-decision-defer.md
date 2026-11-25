# BG1754: A story moved to Blocked by decision defer --block stays Blocked after its last blocking decision is resolved

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_decision.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** an independent reviewer's verdict in run twenty-six (RUN-01M87B5M), recorded as non-blocking and pre-existing at the unit's base (BG1335, engineering seat, verdict dc661386c2cf-328e7e0b)
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T08:32:42Z

## Summary

`sprint decision defer --block` moves a story to Blocked. Resolving the last blocking decision clears the run state's block, but the story's own status stays Blocked, so it never returns to the batch on its own. Also `deferred_units` drops the unit when its first decision is answered, even if another is still open.

## Steps to Reproduce

1. `sprint decision defer --block` a question for a story in the batch.
2. `sprint decision resolve` it.
3. The story's status is still Blocked.

## Proposed Fix

On the last blocking decision's resolve, restore the status the story held before the block, and keep a unit in `deferred_units` while any of its decisions is open.

## Acceptance Criteria

- [ ] **AC1** Given a story moved to Blocked by `decision defer --block`, when its last blocking decision is resolved, then its status returns to the status it held before the block, and `deferred_units` keeps the unit while any of its decisions is open. Fails on: the story left Blocked, or the unit dropped from `deferred_units` with a decision still open.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
