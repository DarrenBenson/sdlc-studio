# CR-0712: Prevent or retire lesson LC-010 (the push gate and CI disagree on the runner)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M7GEHM close, 2026-11-16T03:51:22Z

## Summary

The failure class LC-010 (the push gate and CI disagree on the runner) recurred 2 time(s) after it was recorded in RUN-01M3BK9Y, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A test is green only under the runner CI uses.

Behaviour asked of the agent: Before pushing a new test module, run it under `python3 -m unittest` as well as pytest, and prefer one runner at push and in CI (BG0770).

Hits:

- RUN-01M3VF2J on US0977 (retro:RETRO0129)
- RUN-01M7GEHM on BG1489 (retro:RETRO0147)

## Impact

Every lane and review the class reaches: each repeat of LC-010 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-010 describes cannot recur there: RUN-01M3VF2J on US0977; RUN-01M7GEHM on BG1489.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-010 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Raised |
