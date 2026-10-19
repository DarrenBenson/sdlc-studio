# BG1067: The triage session cap keys on the run state's id whether or not the run is sealed, so a signed run's counter keeps charging every later session's findings

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_session_after_sign.py, changelog.d/BG1067.md, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py
> **Evidence:** 2026-10-19 refusal: 'file refused: triage session cap reached (40 findings filed this session) - ... The counter is keyed on 'RUN-01M4R168''; sdlc-studio/.local/run-state.json outcome goal-reached (signed 2026-10-16, RPT0020); triage_noise.py:107-118.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:50:02Z

## Summary

`triage_noise._session_key` (`triage_noise.py`:84-118) documents its second source as 'The OPEN RUN's id', but reads `run_state.read(root)['run_id']` with no check of the outcome. After `sprint sign` the run state still names the sealed run, so the counter neither resets at the sign nor falls through to the date key: RUN-01M4R168 was signed on 2026-10-16, and on 2026-10-19 a unified review's sixth finding was refused with 'triage session cap reached (40 findings filed this session) ... keyed on RUN-01M4R168'.

## Steps to Reproduce

1. Sign a run (`sprint.py sign`). 2. On a later day, with no run opened, file findings with `file_finding.py file` -> they count against the signed run's key, and the cap refuses once the run's total reaches 40.

## Proposed Fix

Return the run id only while the run is open (its outcome not in `run_state.CLOSED`); otherwise fall through to the date key, as the docstring says.

## Acceptance Criteria

- [ ] **AC1** After a run is signed, findings filed with no run open are counted under the date key, not the sealed run's id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_session_after_sign.py -k sealed_run_does_not_key_the_session

## Impact

Work after a signed run, such as a review or triage, inherits the run's whole filing budget and is refused for findings it never filed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
