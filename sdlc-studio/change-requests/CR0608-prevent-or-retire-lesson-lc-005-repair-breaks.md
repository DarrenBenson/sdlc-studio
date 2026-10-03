# CR-0608: Prevent or retire lesson LC-005 (repair breaks its neighbour)

> **Status:** Complete
> **Decomposed-into:** EP0272
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M3Y7DP close, 2026-10-02T15:05:18Z

## Summary

The failure class LC-005 (repair breaks its neighbour) recurred 3 time(s) after it was recorded in back-to-basics-review, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A repair is proven only on the paths beside the one it was written for.

Behaviour asked of the agent: After a fix, probe the neighbouring inputs and every caller of what changed, and run the full suite before calling it done.

Hits:

- RUN-01M3891F on US0887 (retro:RETRO0122)
- RUN-01M3VF2J on BG0839 (retro:RETRO0129)
- RUN-01M3Y7DP on BG0895 (retro:RETRO0130)

## Impact

Every lane and review the class reaches: each repeat of LC-005 has cost a review round, 3 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-005 describes cannot recur there: RUN-01M3891F on US0887; RUN-01M3VF2J on BG0839; RUN-01M3Y7DP on BG0895.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-005 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Raised |
