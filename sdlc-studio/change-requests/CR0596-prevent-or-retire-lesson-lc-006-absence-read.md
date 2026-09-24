# CR-0596: Prevent or retire lesson LC-006 (absence read as an answer)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M39MC0 close, 2026-09-24T18:56:22Z

## Summary

The failure class LC-006 (absence read as an answer) recurred 2 time(s) after it was recorded in back-to-basics-review, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: An absent, empty or unreadable input is not an answer: fail loud and name it.

Behaviour asked of the agent: Tell missing, empty and unreadable apart in the code path, report each by name, and never print a success the tool did not achieve.

Hits:

- RUN-01M39MC0 on US0892 (critic:RUN-01M39MC0): --maxschedchunk arrived in pytest-xdist 3.2.0, so on an older xdist every gate.py --run-tests exits 4 and the push's full-suite lane blocks every push, and the refusal names no reason [LC-006]
- RUN-01M39MC0 on US0898 (critic:RUN-01M39MC0): non-blocking: the write refusals for a missing notes file or no count line are unpinned [LC-006]

## Impact

Every lane and review the class reaches: each repeat of LC-006 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-006 describes cannot recur there: RUN-01M39MC0 on US0892; RUN-01M39MC0 on US0898.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed, LC-006 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure reads `retired` instead.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Raised |
