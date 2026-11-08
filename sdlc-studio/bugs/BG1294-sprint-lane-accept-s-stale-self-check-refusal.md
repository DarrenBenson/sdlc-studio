# BG1294: `sprint lane accept`'s stale-self-check refusal tells the operator to land the unit again, which `lane land` refuses after an out-of-band repair, and its refusal prints a doubled full stop

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py
> **Evidence:** BG1290 round-2 review (qa-seat-BG1290-r1), probes P6, P6b and P0c, verdict in scratchpad rel63/lanes/BG1290-verdict-r2.txt
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T18:17:49Z

## Summary

From BG1290's round-2 review (qa-seat-BG1290-r1, non-blocking). Under `review.author_self_check: block`, `lane accept` refuses a unit whose Affects changed after its self-check and says to "land US0101 again with its self-check handed in" (lanes.py:345-348). In AC4's own case, a repair that reached main with no `lane land`, a fresh lane has nothing staged and no commit ahead of main, so `sprint lane land` refuses with "there is nothing to land" (probe P6). The remedy works only through an empty commit (`git commit --allow-empty` in a fresh `lane-us0101`, landed with the hand-in: probe P6b), which the message does not mention. Separately, lanes.py:330 appends ". A verdict is recorded only" to `why.strip()`, so a refused self-check prints "Nothing was written.. A verdict is recorded only" (probe P0c, introduced in b00deeaa).

## Steps to Reproduce

In a throwaway repo: land US0101 through `sprint lane land` with its self-check, then commit a repair to its Affects as `fix(US0101)` with no `lane land`. Under `block`, `sprint lane accept --unit US0101` exits 2 naming the stale self-check; follow its advice with a fresh `lane-us0101` worktree and `lane land`, which refuses with nothing to land.

## Proposed Fix

Name a remedy that works for an out-of-band repair: either re-record the self-check with `critic.py self-check record` and re-brief with `critic.py brief`, or say how to land the repair (an empty commit with the hand-in). Strip a trailing full stop from `why` before joining the sentence.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From BG1290's round-2 review (qa-seat-BG1290-r1, non-blocking).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a throwaway repo: land US0101 through `sprint lane land` with its self-check, then commit a repair to its Affects as `fix(US0101)` with no `lane land`.
- [ ] **AC3** The proposed fix lands, pinned by a test: Name a remedy that works for an out-of-band repair: either re-record the self-check with `critic.py self-check record` and re-brief with `critic.py brief`, or...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
