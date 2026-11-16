# BG1490: test_critic_rejoinder_from_ledger and test_critic_verdict_file_binding fail when run inside an agent session, because the harness session id reaches the verdict's source field

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py, changelog.d/BG1490.md
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

- [ ] **AC1** The behaviour described is corrected: Run fourteen's BG1489 builder found that `test_critic_rejoinder_from_ledger.py` and `test_critic_verdict_file_binding.py` fail when run from inside a Claude...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: From inside an agent session (with the harness's session variable set), run pytest...
- [ ] **AC3** The proposed fix lands, pinned by a test: Scrub the harness session variables the verdict recorder reads in the tests' shared environment helper, and add a test that sets one and shows the recorded...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
