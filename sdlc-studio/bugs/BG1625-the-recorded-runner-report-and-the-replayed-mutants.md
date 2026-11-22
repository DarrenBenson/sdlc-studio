# BG1625: The recorded runner report and the replayed mutants: a -k 'a or b' selector prints bogus ids, a malformed kept list crashes the brief, a failed list write is reported as nothing written, and several checks have no test

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1625.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py
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

- [ ] **AC1** Given a Verify line using `-k 'a or b'`, when `critic.py brief` prints the replay of the author's mutants, then it prints the real selected tests or refuses the expression by name, never ids such as `a` and `b` as selectors. Fails on: bogus selectors printed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py::CriticReplaySelectorTests

- [ ] **AC2** Given a read-only sdlc-studio/reviews/author-mutants/ directory, when `critic.py self-check record --mutants-from <report>` runs, then it exits non-zero saying the kept list was not written and adds no self-check row; a malformed kept list is refused with a named error, not a crash. Fails on: the row added while the message says nothing was written, and a malformed kept list crashing the brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py::CriticKeptListWriteTests

- [ ] **AC3** Given a kept list written for a unit, when its file is read, then it holds a path relative to the repository root, and a report of the wrong kind or version is refused. Fails on: an absolute local path in a committed file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py::CriticKeptListPathTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-22 | Claude Sonnet 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-two) |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Re-sized 3 to 5 for planning: three criteria cover three separate behaviours (the -k expression replay, the kept-list write failure and the kept list's relative path) |
