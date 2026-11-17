# BG1490: test_critic_rejoinder_from_ledger and test_critic_verdict_file_binding fail when run inside an agent session, because the harness session id reaches the verdict's source field

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/gitutil.py, .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py, changelog.d/BG1490.md
> **Evidence:** Run fourteen BG1489 builder hand-back, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T01:15:00Z

## Summary

Run fourteen's BG1489 builder found that `test_critic_rejoinder_from_ledger.py` and `test_critic_verdict_file_binding.py` fail when run from inside a Claude Code agent session: the session id from the environment is written into each recorded verdict's source field, so the tests' expected `provenance unknown` does not match. They pass on the gate host and CI, which run without the harness variables. A test that reads the harness's environment is not isolated: the shared test base should scrub the session variables the recorder reads, as it scrubs the git environment.

## Steps to Reproduce

From inside an agent session (with the harness's session variable set), run pytest .claude/skills/sdlc-studio/scripts/tests/`test_critic_rejoinder_from_ledger.py.`

## Proposed Fix

Scrub the harness session variables the verdict recorder reads in the tests' shared environment helper, and add a test that sets one and shows the recorded source is unaffected.

## Acceptance Criteria

- [ ] **AC1** Given `CLAUDE_CODE_SESSION_ID` set in the test process's environment, as it is inside an agent session, when a binding test records a verdict through `critic.py record`, then the recorded source cell is the one recorded with the variable unset. Fails on: the harness session id reaching the verdict's source field.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_a_harness_session_variable_does_not_reach_the_recorded_source
- [ ] **AC2** Given the same variable set, when the rejoinder tests record a verdict and read the rejoinder from the ledger, then the row and the rejoinder are the ones produced with the variable unset. Fails on: `test_critic_rejoinder_from_ledger.py` reading red inside an agent session and green on the gate host.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_a_harness_session_variable_does_not_change_the_recorded_row
- [ ] **AC3** Given harness session variables in the ambient environment, when `gitutil.git_env` builds a child environment, then none of the variables the verdict recorder reads is in it, and a variable the caller passes as an extra is still there. Fails on: a scrub that misses a variable the recorder reads, or one that drops a value a provenance test set on purpose.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::HarnessSessionScrubTests::test_the_session_variables_are_dropped_and_an_explicit_extra_is_kept

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
