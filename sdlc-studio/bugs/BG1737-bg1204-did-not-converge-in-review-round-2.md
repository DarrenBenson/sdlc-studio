# BG1737: BG1204 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, changelog.d/BG1204.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T11:55:00Z

## Summary

BG1204 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [regression] A Codex lane run's delegated total is still dropped from a mixed run's total, the round-one defect under another harness. The repair leaves `claude` untagged and tags every other harness (sprint.py:9889), and `subagent_readers` (run\_state.py:2806) names any harness whose closing stamp holds subagents. The Codex reader leaves lane worktrees out by design: meter\_codex.py:27-29 says a thread under `lanes.RUN_WORKTREES`, where `sprint lane run --harness codex` runs `codex exec`, "is left out, since a lane's spend reaches the run once, through its delegated record". Probe through `sprint._lane_run_totals` with a `codex` reading of 1000 tokens, a main-thread-only Claude session and a Codex session whose stamps hold a spawned thread: at 0de7cc652 the record is tagged `codex`, `subagent_readers` is `{'codex'}`, `_run_tokens_actual` is (4600, 0) and the page `tokens_total` is 4600. The same probe at base 3994fa77 gives (5600, 1) and 5600. The lane's 1000 tokens are in no reading, so they are now counted nowhere. AC1 asks the exclusion only for `opencode`, so excluding `codex` is the implementation's choice, not a criterion. No test covers a `codex`-tagged lane record; RULINGS: Round-one finding "A Claude Code lane run's delegated total is now dropped from a mixed run's total": CLOSED for Claude. A `claude` lane reading now writes an untagged record, my round-one probe re-run at 0de7cc652 gives (5600, 1) and 5600, and `test_a_claude_code_lane_run_is_added_in_a_mixed_run` pins it through the Estimates row, the page Tokens figure and the retro total (the author's M1 to M4 and T1 replay killed). The root cause survives for other harnesses, hence the regression above. verify\_ac --dry-run: ac=4 pass=4. test\_run\_state.py: 78 passed. The repaired fragment is TRUE for Claude and for `--delegated-tokens`. For the operator, not the builder, because it follows from the criteria: AC4 tags an `opencode` lane run and AC1 drops an `opencode`-tagged record, but `meter_opencode._dirs` matches only the repo root's own spellings (`directory IN (...)`, meter\_opencode.py:56 and 92-94), while lanes run with their cwd under `sdlc-studio/.local/worktrees` (lanes.py:1414 and 1827). So an `opencode` lane session looks to be in no reading either, and AC1's premise that its spend counts twice may not hold. That is read from the code and not executed against an OpenCode store, so it is UNVERIFIABLE here.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1204 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1204 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [regression] A Codex lane run's delegated total is still dropped from a mixed run's total, the round-one defect under another harness. The repair leaves `claude` untagged and tags every other harness (sprint.py:9889), and `subagent_readers` (run\_state.py:2806) names any harness whose closing stamp holds subagents. The Codex reader leaves lane worktrees out by design: meter\_codex.py:27-29 says a thread under `lanes.RUN_WORKTREES`, where `sprint lane run --harness codex` runs `codex exec`, "is left out, since a lane's spend reaches the run once, through its delegated record". Probe through `sprint._lane_run_totals` with a `codex` reading of 1000 tokens, a main-thread-only Claude session and a Codex session whose stamps hold a spawned thread: at 0de7cc652 the record is tagged `codex`, `subagent_readers` is `{'codex'}`, `_run_tokens_actual` is (4600, 0) and the page `tokens_total` is 4600. The same probe at base 3994fa77 gives (5600, 1) and 5600. The lane's 1000 tokens are in no reading, so they are now counted nowhere. AC1 asks the exclusion only for `opencode`, so excluding `codex` is the implementation's choice, not a criterion. No test covers a `codex`-tagged lane record
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1204 AC1, as narrowed on 2026-11-24, passes: Given a run with a Claude main-thread session, an opencode session stamped includes_subagents True, and a delegated record tagged to the opencode harness, when `_run_tokens_actual` and the page's Tokens figure (both over every session's stamps) are read, then the tagged record is not added and an untagged record still is. Fails on: the whole delegated total is added because `includes_subagents` is an all() over the meters, so the opencode session's delegated spend counts twice.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_a_record_tagged_to_a_subagent_reading_harness_is_not_added
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** BG1204 AC2 still passes: Given a delegated record recorded with a harness, when `record_delegated_tokens` writes it, then the record carries that harness and `delegated_total` can exclude it by harness. Fails on: `record_delegated_tokens` has no harness field, so records cannot be split by harness.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_the_record_carries_its_harness
  - **Verified:** yes (2026-11-24)
- [ ] **AC4** BG1204 AC3 still passes: Given a mixed run whose delegated records are all untagged, when the total is read, then they are added as before. Fails on: a fix that stops adding untagged records understates a Claude-only fan-out.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_untagged_records_are_added_as_before
  - **Verified:** yes (2026-11-24)
- [ ] **AC5** BG1204 AC4, as re-ruled on 2026-11-24, passes: Given `sprint.py lane return` recording a lane run's usage under any harness (`claude`, `codex`, `opencode`), when the delegated record is written, then it carries no harness and the run's total adds it, because no shipped reader counts a lane worktree's session. Fails on: the call site tagging the lane's harness, which `subagent_readers` then drops.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_a_lane_run_return_leaves_its_record_untagged
  - **Verified:** yes (2026-11-24)
- [ ] **AC6** BG1204 AC5 passes: Given `retro.py` recording a delegated total with `--delegated-tokens 300 --delegated-harness opencode` in a run whose opencode session's reading holds its subagents, when the run's total is read (`_run_tokens_actual`, the page's Tokens figure and retro's accuracy total), then the 300 is not added; the same record without `--delegated-harness` is added as before; a `--delegated-harness` naming no known harness is refused with nothing recorded; and help/sprint.md names the flag beside `--delegated-tokens`. Fails on: no shipped command writing a harness-tagged record, so AC1's exclusion is reachable only through the Python API and the double count in this bug's title still happens (round three's qa probe: a 300-token record beside such a session read 4900 at HEAD and at base).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_a_delegated_total_recorded_with_its_harness_is_not_added_twice
  - **Verified:** yes (2026-11-24)
- [ ] **AC7** BG1204 AC6 passes: Given the same run, when retro's accuracy total is read from one capture (`accuracy --tokens-from-harness`), then a record tagged to a harness is left out only when that capture is that harness's own reading and holds its subagents, and the basis then says adding it would count that spend twice; under a capture of another harness (a Claude close beside an opencode-tagged record) the record is added, since that figure does not read the tagged harness's session, and no sentence says it is already counted. Fails on: a Claude capture of 4,000 leaving an opencode-tagged 300 out, so the retro states a figure that holds that spend nowhere, and the basis calling it counted twice (round five's qa probe).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DelegatedHarnessTests::test_a_capture_of_another_harness_adds_a_tagged_record
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | sdlc-studio | Filed |
| 2026-11-24 | orchestrator (delegate under D0545) | AC5 follows BG1204's re-ruled AC4 (committed in b092b3e1d): every lane-run record stays untagged, verified by the round-three test; the copied AC4 named a test the re-ruling retires (the SP2 builder) |
| 2026-11-24 | orchestrator (delegate under D0545) | AC6 mirrors BG1204's new AC5: round three's qa found no shipped command writes a harness-tagged record (retro.py, sprint.py's two lane returns all pass none), so the title's double count was unfixed on every path a user reaches. The fix is completed through `retro.py --delegated-harness` rather than the fragment reworded to a Fixed that is not true |
| 2026-11-24 | orchestrator (delegate under D0545) | AC2 follows BG1204's narrowed AC1 and AC7 mirrors its new AC6: round five's qa showed the retro's accuracy total is one capture (the closing session's main thread), so leaving a tagged record out of it is right only when that capture is the tagged harness's own reading; under a Claude close the opencode-tagged spend was in no stated figure. AC1 keeps the exclusion over every session's stamps; the new criterion rules the one-capture total |
