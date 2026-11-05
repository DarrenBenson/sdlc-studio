# BG1231: lane land: exit 1 documented too narrowly, two test gaps, a false --units help line, and an unscrubbed git environment

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_followups.py, changelog.d/BG1231.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run six reviews, scratchpad run6/*-verdict-r*.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T15:34:25Z

## Summary

2026-11-05, US1118's build and review. Exit 1 is documented as a stopped landing or an unbriefed unit but is also returned when the lane lands and the worktree is kept (lanes.py near 222; help/sprint.md near 584); a mutant that continues after a refused commit (lanes.py near 209) passes and prints that the lane stays committed; hardcoding the review tier (lanes.py near 186) passes; the --units help says it defaults to the batch but lane land refuses without it (sprint.py near 12522); lanes.py passes the inherited git environment (`GIT_DIR` and the like) unscrubbed.

## Steps to Reproduce

See the summary; each item was reproduced by its reviewer or builder.

## Proposed Fix

Document every exit-1 case, pin the refused-commit stop and the tier, correct the --units help, and scrub the git environment.

## Acceptance Criteria

- [ ] **AC1** Every exit-1 case is documented; a refused commit stops the landing and a mutant that continues fails a test; the tier is read, not assumed; lane land with `GIT_DIR` set lands the right repository.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_followups.py

## Impact

Misleading docs and two behaviours no test holds.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
