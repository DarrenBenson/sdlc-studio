# BG0647: test_config's status integration test gathers status over the REAL repository, so the suite's duration and its noise count depend on this tree's state

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`IntegrationTests.test_status_reads_config` in `test_config.py` calls status.gather(Path('.')) over whatever repository the suite runs in. On this corpus that is 72 to 113 seconds in one test, and every diagnostic the real tree makes status print - on 2026-09-04, twelve 'closure with no separator' warnings from the repair ledger while a run is open - lands in the green-run noise count, which is how a full local run reads 118 against a baseline of 106 while nothing in the diff leaks. The count therefore differs between a clone with an open run and CI, which has no .local state. Found bisecting the noise gate during BG0643's delivery.

## Steps to Reproduce

1. PYTHONPATH=.claude/skills/sdlc-studio/scripts/tests python3 -m unittest `test_config.IntegrationTests.test_status_reads_config` 2>&1 | python3 tools/`test_noise.py` --baseline 0. 2. Observe about 72 s and the closure warnings counted as leaks.

## Proposed Fix

Point the test at a fixture workspace that carries a config-defaults.yaml (the claim is that status consumes the config, which a two-artefact fixture proves in under a second), and capture its output. Keep one smoke over the real tree only where a criterion needs it, and never inside the noise-gated suite.

## Acceptance Criteria

- [ ] **AC1** Given the suite runs in this repository, when `test_status_reads_config` runs, then it gathers a fixture workspace, completes in under two seconds and prints nothing
  - **Verify:** manual - the executable verifier is authored when this is groomed; the test it re-authors is the one named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
