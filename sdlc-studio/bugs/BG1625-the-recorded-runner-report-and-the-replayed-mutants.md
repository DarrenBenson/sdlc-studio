# BG1625: The recorded runner report and the replayed mutants: a -k 'a or b' selector prints bogus ids, a malformed kept list crashes the brief, a failed list write is reported as nothing written, and several checks have no test

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1625.md
> **Evidence:** round two of the qa seat on US1201 (sdlc-studio/reviews/verdicts/US1201/7168f002079e-b8ab7ed8.txt): the same report passed to both --mutants-from and --mutants is counted twice (killed 6), and the lane brief's rewritten hand-in note (sprint.py around 3349) has no test
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T17:26:26Z

## Summary

Non-blocking findings from both seats' reviews of the recorded runner report (self-check --mutants-from) and the replay of the author's mutants in the QA brief (run eighteen). A Verify line using -k 'a or b' prints bogus selectors (critic.py around 2947). The kept list stores an absolute local path in a committed file. If writing the kept list fails, the self-check row is still added while the message says nothing was written (critic.py around 3274-3279). A malformed kept list crashes the brief (critic.py around 3394). The replay runs before the self-check gate refuses a brief, and a --rejoinder brief carries no replay. Untested: the report's kind and version refusals (critic.py around 3318-3321), the rule keeping the kept list out of the Affects digest (critic.py around 3016), the replay's 'not run' branch, and the report name in lane land's preflight owner check (lanes.py around 591). Pre-existing (US1088): --mutants accepts the report object.

## Steps to Reproduce

Record a self-check whose kept-list write fails (a read-only sdlc-studio/reviews/author-mutants/): the row is added and the message says nothing was written.

## Proposed Fix

Store a root-relative path; roll the row back or say the write failed; refuse a malformed kept list with a named error; gate before replaying; decide and state whether a rejoinder replays; add a failing-first test per check; parse -k expressions or refuse them.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from both seats' reviews of the recorded runner report (self-check --mutants-from) and the replay of the author's mutants in the QA brief...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record a self-check whose kept-list write fails (a read-only sdlc-studio/reviews/author-mutants/): the row is added and the message says nothing was written.
- [ ] **AC3** The proposed fix lands, pinned by a test: Store a root-relative path; roll the row back or say the write failed; refuse a malformed kept list with a named error; gate before replaying; decide and state...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
