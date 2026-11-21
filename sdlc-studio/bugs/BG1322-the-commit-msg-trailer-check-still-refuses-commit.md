# BG1322: The commit-msg trailer check still refuses commit 089008d5's `Refs: US1090`, whose only record is a waiver row in decisions.md

> **Status:** Won't Fix
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

- [ ] **AC1** Given a commit whose subject names several ids, whose staged `sdlc-studio/decisions.md` adds a waiver row for one of them, and whose `Refs:` line names that unit (commit 089008d5's message and paths, replayed), when the commit-msg hook runs, then the commit is accepted and the line is kept. Fails on: `Refs: US1090` refused as naming a unit that owns no staged file.
  - **Verify:** pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_waiver_row_added_for_a_unit_attributes_its_refs_line
- [ ] **AC2** Given a commit that adds a decision row which only mentions a unit in its prose, or stages `decisions.md` with that unit's waiver row already in it and untouched, when `derive_trailers` judges a `Refs:` line naming the unit, then the line is still listed as contradicted. Fails on: any mention of an id in the decisions log counting as ownership.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::RefsTrailerAttributionTests::test_a_decision_row_that_only_mentions_a_unit_owns_nothing

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it is what is left of a fix already shipped. One historic commit, 089008d5, is still refused at replay; the repair shipped and no new commit meets it. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
