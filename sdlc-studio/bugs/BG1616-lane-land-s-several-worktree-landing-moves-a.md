# BG1616: lane land's several-worktree landing moves a body line shaped like a trailer into the trailers, and three of its refusals have no test

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1616.md
> **Evidence:** round two of the engineering seat on the repair (sdlc-studio/reviews/verdicts/US1192/56bc2b908958-a142de19.txt) adds: the refusal of a later worktree with commits ahead advises naming that worktree first, and no test pins the behaviour that advice relies on (the mutant at lanes.py around 397 survived)
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:54:34Z

## Summary

Non-blocking findings from the qa review of the several-worktree land (run eighteen): a commit-message body line such as `Note: ...` is read as a trailer and moved into the trailer block, and three of the land's refusals are reached by no test.

## Steps to Reproduce

Land two worktrees whose commit-msg.txt body holds a line `Note: keep this`; the commit's trailer block carries it.

## Proposed Fix

Treat only known trailer keys, or only the final paragraph, as trailers; add a test per refusal.

## Acceptance Criteria

- [ ] **AC1** Given two worktrees whose commit-msg.txt hold a body paragraph `Note: keep this` placed last, before the `Refs:` trailer paragraph, when `_combined_message` joins them, then `Note: keep this` stays in the body and the trailer block holds only the known trailers (`Refs:`, `Mentions:`). Fails on: the last paragraph is moved into the trailers whenever every line matches `_TRAILER`, so the note joins `Refs:` (reproduced at HEAD).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_body_line_shaped_like_a_trailer_stays_in_the_body
  - **Verified:** yes (2026-11-25)
- [ ] **AC2** Given the same two worktrees with a real `Refs: BG1616` and `Mentions: X` trailer paragraph, when they are joined, then both trailers still reach the trailer block once each (positive control). Fails on: a fix that stops reading any trailer.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_known_trailers_still_reach_the_trailer_block
  - **Verified:** yes (2026-11-25)
- [ ] **AC3** Given a later worktree holding commits ahead of main, when the land refuses and the operator re-runs it naming that worktree first, then the land succeeds, which is what the refusal's advice relies on. Fails on: no test pins the advised re-run (the test at test_lane_land.py:1589 pins only the refusal).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_naming_a_worktree_with_commits_ahead_first_lands_it
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: criteria now pin the trailer and the advised re-run; the overlap refusal (test_lane_land.py:1545) and the named-twice refusal (:1573) already have tests at HEAD, so only the commits-ahead advice is left untested |
