# BG1204: A run metered by two harnesses adds the supplied delegated totals in full, even over a reading that already holds delegated spend

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/BG1204.md
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
- [ ] **AC4** Given `sprint.py lane return` recording a lane run's usage under any harness (`claude`, `codex`, `opencode`), when the delegated record is written, then it carries no harness and the run's total adds it, because no shipped reader counts a lane worktree's session: a `claude -p` lane is its own session, the Codex reader leaves threads under the lane worktrees out, and the OpenCode reader matches only the repository root's own directory. Fails on: the call site tagging the lane's harness, which `subagent_readers` then drops, so the lane's spend is counted nowhere (round two's qa probe: a `codex` lane run of 1000 tokens read 4600 where the base read 5600).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_a_lane_run_return_leaves_its_record_untagged
- [ ] **AC5** Given `retro.py` recording a delegated total with `--delegated-tokens 300 --delegated-harness opencode` in a run whose opencode session's reading holds its subagents, when the run's total is read (`_run_tokens_actual`, the page's Tokens figure and retro's accuracy total), then the 300 is not added; the same record without `--delegated-harness` is added as before; a `--delegated-harness` naming no known harness is refused with nothing recorded; and help/sprint.md names the flag beside `--delegated-tokens`. Fails on: no shipped command writing a harness-tagged record, so AC1's exclusion is reachable only through the Python API and the double count in this bug's title still happens (round three's qa probe: a 300-token record beside such a session read 4900 at HEAD and at base).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_a_delegated_total_recorded_with_its_harness_is_not_added_twice

## Impact

A mixed-harness run can overstate its tokens.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: re-read at HEAD (the addition is in sprint_report and retro, not run_state); ACs name a harness tag and its tests; 3 pts |
| 2026-11-24 | orchestrator | AC4 and sprint.py added: the RS builder found no caller passes the harness tag; the lane-run return in sprint.py already holds the harness, so it passes it there (one call site; lane SP replays over it) |
| 2026-11-24 | orchestrator (delegate under D0545) | AC4 re-ruled: a lane run's delegated record carries no harness under any harness, since no shipped reader counts a lane worktree's session (meter_codex leaves `RUN_WORKTREES` out; meter_opencode `_dirs` matches the repository root only; a `claude -p` lane is its own session). The first AC4, which this orchestrator added in the build, tagged non-Claude lane runs and lost their spend (round-two qa, carried as BG1737) |
| 2026-11-24 | orchestrator (delegate under D0545) | AC5 added and help/sprint.md joins the Affects: round three's qa found no shipped command writes a harness-tagged record (retro.py, sprint.py's two lane returns all pass none), so the title's double count was unfixed on every path a user reaches. The fix is completed through `retro.py --delegated-harness` rather than the fragment reworded to a Fixed that is not true |
