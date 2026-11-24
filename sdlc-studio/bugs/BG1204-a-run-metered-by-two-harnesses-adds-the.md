# BG1204: A run metered by two harnesses adds the supplied delegated totals in full, even over a reading that already holds delegated spend

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG1204.md
> **Evidence:** US0991 round-1 verdict, scratchpad run5/US0991-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T12:39:24Z

## Summary

2026-11-04, US0991's review (pre-existing). With a Claude main-thread session and an opencode session stamped subagents True, `run_token_total` gives `includes_subagents` False (an all() over the meters), so `sprint_report._run_tokens_actual` and `retro.py` (`delegated_total`) add the supplied delegated total in full on top of the opencode reading, which may count that spend twice, while the basis calls the total a lower bound. Delegated records name no harness, so they cannot be split. Re-read at HEAD cecc9dfe7: `run_token_total` itself adds nothing; the addition is in those two callers. Still real: `record_delegated_tokens` has no harness field.

## Steps to Reproduce

1. A run with one Claude session (main thread only) and one opencode session stamped subagents True, plus a supplied delegated total.
2. `run_token_total` adds the whole delegated total.

## Proposed Fix

Tag each delegated record with the session or harness it was spent under, and add it only to a reading that cannot see it.

## Acceptance Criteria

- [ ] **AC1** Given a run with a Claude main-thread session, an opencode session stamped includes_subagents True, and a delegated record tagged to the opencode harness, when `_run_tokens_actual` and retro's accuracy total are read, then the tagged record is not added and an untagged record still is. Fails on: the whole delegated total is added because `includes_subagents` is an all() over the meters, so the opencode session's delegated spend counts twice.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_a_record_tagged_to_a_subagent_reading_harness_is_not_added

- [ ] **AC2** Given a delegated record recorded with a harness, when `record_delegated_tokens` writes it, then the record carries that harness and `delegated_total` can exclude it by harness. Fails on: `record_delegated_tokens` has no harness field, so records cannot be split by harness.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_the_record_carries_its_harness

- [ ] **AC3** Given a mixed run whose delegated records are all untagged, when the total is read, then they are added as before. Fails on: a fix that stops adding untagged records understates a Claude-only fan-out.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_untagged_records_are_added_as_before

## Impact

A mixed-harness run can overstate its tokens.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: re-read at HEAD (the addition is in sprint_report and retro, not run_state); ACs name a harness tag and its tests; 3 pts |
