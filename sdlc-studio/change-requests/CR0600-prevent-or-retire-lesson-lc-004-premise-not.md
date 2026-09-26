# CR-0600: Prevent or retire lesson LC-004 (premise not executed)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M3CK1K close, 2026-09-26T15:46:18Z

## Summary

The failure class LC-004 (premise not executed) recurred 2 time(s) after it was recorded in back-to-basics-review, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: Verify a premise by execution before filing, planning or fixing on it.

Behaviour asked of the agent: Run the repro or the Given at HEAD and quote its output; decide regression versus pre-existing with git log -S, never by impression.

Hits:

- RUN-01M3BK9Y on BG0756 (critic:RUN-01M3BK9Y): MOVED: refine sizes it reappears in test\_lean\_cr\_filing.py, test\_two\_backlogs.py and US0128's revision row, outside AC3's scan (3 lines) [LC-004]
- RUN-01M3CK1K on BG0731 (critic:RUN-01M3CK1K): non-blocking: the commit message credits CR0592 to the shipped default, but this repo's own config sets the key (US0926) [LC-004]

## Impact

Every lane and review the class reaches: each repeat of LC-004 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-004 describes cannot recur there: RUN-01M3BK9Y on BG0756; RUN-01M3CK1K on BG0731.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed, LC-004 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure reads `retired` instead.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Raised |
