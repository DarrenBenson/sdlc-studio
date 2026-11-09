# BG1322: The commit-msg trailer check still refuses commit 089008d5's `Refs: US1090`, whose only record is a waiver row in decisions.md

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, tools/tests/test_commit_msg_mentions.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** BG1264-verdict-r1 and the replay log scratchpad/replay-before.txt (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T17:42:26Z

## Summary

From BG1264's QA review (qa-seat-BG1264-r1, 2026-11-09). Replaying the 60 multi-id commits BG1264's step (2) names, the base refuses 21 and HEAD (after US1133 and BG1264) refuses 1 and rewrites none. The one still refused is 089008d5, whose `Refs: US1090` is recorded only by a waiver row in sdlc-studio/decisions.md, which the check does not read as attribution. BG1264's Summary names this case, so it is filed on its own rather than left implied by BG1264's Fixed.

## Steps to Reproduce

1. Replay commit 089008d5's message and staged paths through `.githooks/commit-msg` in a scratch clone.
2. It refuses the `Refs: US1090` line as unattributed.

## Proposed Fix

Read a decision row that names a unit as a waiver for it as attribution for that unit's `Refs:`, or rule that such a commit carries a `Mentions:` line; pin the replay of 089008d5 with a test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From BG1264's QA review (qa-seat-BG1264-r1, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Read a decision row that names a unit as a waiver for it as attribution for that unit's `Refs:`, or rule that such a commit carries a `Mentions:` line; pin the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
