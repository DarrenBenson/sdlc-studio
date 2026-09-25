# CR-0598: Prevent or retire lesson LC-003 (mechanism reaches no caller)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M3BK9Y close, 2026-09-25T12:19:57Z

## Summary

The failure class LC-003 (mechanism reaches no caller) recurred 2 time(s) after it was recorded in back-to-basics-review, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A mechanism is not delivered until the command people actually run calls it.

Behaviour asked of the agent: Exercise every claim through the shipped CLI entry point in a throwaway fixture, and pin the reader of a derivation, not only the function that derives it.

Hits:

- RUN-01M39MC0 on US0899 (critic:RUN-01M39MC0): a retro, review or handoff with no index row now passes the reconcile lane, which exempts every missing-row whatever the type while settle never applies meta indexes, and the detail claims settle fixes it [LC-003]
- RUN-01M3BK9Y on US0912 (critic:RUN-01M3BK9Y): non-blocking: row\_staleness has no production caller and mutation.py comments now false [LC-003]

## Impact

Every lane and review the class reaches: each repeat of LC-003 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-003 describes cannot recur there: RUN-01M39MC0 on US0899; RUN-01M3BK9Y on US0912.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed, LC-003 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure reads `retired` instead.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Raised |
