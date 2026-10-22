# BG1111: The session token meter sums every usage record, but the harness repeats a message's usage on each of its content blocks, so a run's measured tokens are about 2.5 times what it spent

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_session_tokens_once_per_message.py, changelog.d/BG1111.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** Cost investigation, 2026-10-21. The transcript acd73b30 has 7,794 usage records and 3,343 distinct ids. RUN-01M59TRM's window has a de-duplicated main thread of 3,767,175 tokens, against the 10,098,487 RETRO0135 records. The window's subagents (12 reviews) used a further 5,686,249, which BG0252 already documents the meter omits.
> **Created:** 2026-10-21
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-21T13:33:31Z

## Summary

`run_state.session_tokens` adds input, output and cache-creation tokens over every transcript record that carries usage. The harness writes one record per content block of an assistant message (thinking, text, each tool call), and every one of them carries that message's full usage. This session's transcript holds 7,794 usage records for 3,343 distinct message ids. Summed per record, the main thread cost 49.6M tokens; summed once per message id, 19.7M. RETRO0135 records RUN-01M59TRM at 10,098,487 tokens, but the same window de-duplicated is 3,767,175. The inflation grows with tool calls per message, so it is not even a constant factor: 1.4 to 2.7 times per day. Every VELOCITY row, the tokens-per-point rate and each plan's forecast are built on it.

## Steps to Reproduce

Read any session transcript: count records whose message carries usage, and count distinct `message.id`. The record count is about 2.3 times the id count, and `session_tokens` returns the larger sum.

## Proposed Fix

Count each assistant message once, keyed on `message.id`, as a record with no id is today. Re-derive the recorded actuals, or mark each earlier VELOCITY row as measured on the old basis so the rate does not mix the two.

## Acceptance Criteria

- [ ] **AC1** A transcript in which one message's usage is repeated on three records is counted once, and two distinct messages are counted twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_session_tokens_once_per_message.py::SessionTokensOncePerMessageTests::test_a_repeated_message_is_counted_once

## Impact

Runs read 2-3 times more expensive than they were, and the forecast inherits the error. An operator judging cost, or a retro judging an estimate, works from a number that is wrong by a factor that changes with how parallel the session was.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-21 | Claude Opus 5.5 | Filed |
| 2026-10-22 | sdlc | Correction (US1087 QA review, 2026-10-22): 2a1a0fdd's D0386 paragraph names tree 20fc1a57, the tree of its worktree original e503255e; the cherry-pick on main has tree 9900ea5a, proven only within the next push tip |
