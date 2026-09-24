# CR-0597: Prevent or retire lesson LC-008 (constraint added without retirement)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M39MC0 close, 2026-09-24T18:56:23Z

## Summary

The failure class LC-008 (constraint added without retirement) recurred 4 time(s) after it was recorded in back-to-basics-review, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A new check, refusal, baseline, ratchet or hand-maintained pin must name the measured yield that justifies it or the constraint it retires; a derived fact is generated, never pinned by hand.

Behaviour asked of the agent: Before adding a check, fix the code path that failed; if a check is still needed, say what it retires, and flag any lane whose refusals catch no real defect for deletion.

Hits:

- RUN-01M39MC0 on US0905 (retro:RETRO0123)
- RUN-01M39MC0 on US0896 (critic:RUN-01M39MC0): non-blocking: the retired-criteria test pins a hand count over the live backlog [LC-008]
- RUN-01M39MC0 on US0901 (critic:RUN-01M39MC0): non-blocking: the commit message overstates the retirement while EXPECTED\_LANES and three new tombstone lists are hand-kept [LC-008]
- RUN-01M39MC0 on US0908 (critic:RUN-01M39MC0): AC3 says the step replaces the lane US0811-US0814 proposed, but those stories are still live Drafts that could add it back [LC-008]

## Impact

Every lane and review the class reaches: each repeat of LC-008 has cost a review round, 4 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-008 describes cannot recur there: RUN-01M39MC0 on US0905; RUN-01M39MC0 on US0896; RUN-01M39MC0 on US0901; RUN-01M39MC0 on US0908.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed, LC-008 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure reads `retired` instead.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Raised |
