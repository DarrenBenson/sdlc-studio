# CR-0595: Prevent or retire lesson LC-002 (criterion words outrun the fixture)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M39MC0 close, 2026-09-24T18:56:20Z
> **Decomposed-into:** US0945

## Summary

The failure class LC-002 (criterion words outrun the fixture) recurred 8 time(s) after it was recorded in back-to-basics-review, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A criterion is met only when its test fails without the behaviour on every case its words cover.

Behaviour asked of the agent: Name the plausible wrong implementation before writing the test, check the fixture can reach it, and ask what the test still passes with the change removed.

Hits:

- RUN-01M3891F on US0885 (retro:RETRO0122)
- RUN-01M39MC0 on US0901 (retro:RETRO0123)
- RUN-01M39MC0 on US0896 (critic:RUN-01M39MC0): US0292 AC4 and BG0627 AC3 still claim what the diff made false and still read Verified yes, while their tests were narrowed underneath them [LC-002]; non-blocking: AC2's words claim more than its Draft fixture shows [LC-002]; non-blocking: the AC1 test stubs gate.py, so gate counting warnings as errors survives [LC-002]
- RUN-01M39MC0 on US0898 (critic:RUN-01M39MC0): AC1's test runs only modules naming known-issues.md or release-notes-v, so a live page-to-corpus comparison that names neither survives [LC-002]
- RUN-01M39MC0 on US0899 (critic:RUN-01M39MC0): a pathspec commit (git commit -- paths) runs the hook on git's temporary index, so settle's restage reaches the commit but not the real index, and the next commit silently reverts the settled epic and indexes and deletes the ledger [LC-002]; non-blocking: the rename skip in \_unstaged is unpinned [LC-002]
- RUN-01M39MC0 on US0901 (critic:RUN-01M39MC0): the AC1 test defines a lane as the lister does, so an inline refusal outside run survives [LC-002]; non-blocking: the awk branch for a same-line rule is unexercised [LC-002]
- RUN-01M39MC0 on US0903 (critic:RUN-01M39MC0): removing the grooming assertion left US0888 AC2's stamped test unable to catch a CR that proposes nothing, which passes it now and failed it at the base [LC-002]; the AC2 test spots a proposed check only by the word check, so a new lane or blocking gate criterion survives [LC-002]; non-blocking: the where branch for a hit naming no unit is untested [LC-002]
- RUN-01M39MC0 on US0907 (critic:RUN-01M39MC0): AC1 says Superseded for an epic while EP0171 is correctly Done, and the test accepts Done for any epic [LC-002]
- RUN-01M39MC0 on US0908 (critic:RUN-01M39MC0): the fail-under-CI clause is unpinned, so a CI runner that loses its 3.10 install would skip the floor silently [LC-002]; non-blocking: the 3.10-before-3.12 step order, a conditional 3.10 step and the enumeration counts are unpinned [LC-002]

## Impact

Every lane and review the class reaches: each repeat of LC-002 has cost a review round, 8 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-002 describes cannot recur there: RUN-01M3891F on US0885; RUN-01M39MC0 on US0901; RUN-01M39MC0 on US0896; RUN-01M39MC0 on US0898; RUN-01M39MC0 on US0899; RUN-01M39MC0 on US0901; RUN-01M39MC0 on US0903; RUN-01M39MC0 on US0907; RUN-01M39MC0 on US0908.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed, LC-002 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure reads `retired` instead.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Raised |
