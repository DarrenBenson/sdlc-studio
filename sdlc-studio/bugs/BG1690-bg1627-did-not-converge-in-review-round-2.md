# BG1690: BG1627 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1627.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_brief_bound_group.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T18:06:49Z

## Summary

BG1627 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the stop grace the brief is given at its bound is pinned only where `_critic` hands it to `_bounded`, not where `_bounded` gives it to the group. The changelog's "given critic's `REPLAY_STOP_GRACE` before SIGKILL" can therefore still be made false with the suite green. The mutant dropping the handed grace in the except branch of `_bounded` (lanes.py:198, `_kill_group(proc, grace)` to `_kill_group(proc)`) survived `test_lane_land_brief_bound_group.py`, including the new `test_the_brief_alone_is_given_critic_s_replay_stop_grace`. It also survived `test_lane_land_commit_timeout_group.py`, `test_kill_grace_interrupt.py` and `test_critic.py -k BriefAuthorMutants`. Two Ctrl-C cases failed on the loaded first run and passed alone under the mutant, so they were load flakes, not kills. The branch is live in isolation. `_bounded(["sh", "-c", ...], 1, 8)` over a member that takes 4 s to stop on SIGTERM lets it stop cleanly at HEAD (5.0 s, its marker written). Under the mutant it is sent SIGKILL at `KILL_GRACE` (3.0 s, no marker). The grace argument of `_bounded` is non-None only for the brief, and the commit's cases cannot tell `KILL_GRACE` from the default, so only a BG1627 case can pin it; RULINGS: Round-1 "no test pins the stop grace for the brief" is MOVED. The round-1 mutant (`grace = None` in `_critic`) is now killed by the new case (author replay killed), but the grace is still unpinned one call further on, as above. AC1 is met: `verify_ac.py run --id BG1627 --dry-run` passes. Claim inventory: the `_critic` docstring and the changelog are TRUE at HEAD by the isolation probe, and the new case's docstring is TRUE. The repair leaves the round-1 pre-existing finding unchanged, and it was not re-probed: critic.py dies on the group's SIGTERM and leaves its `author_mutants_*` work directory. No open bug covers it.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1627 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1627 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the stop grace the brief is given at its bound is pinned only where `_critic` hands it to `_bounded`, not where `_bounded` gives it to the group. The changelog's "given critic's `REPLAY_STOP_GRACE` before SIGKILL" can therefore still be made false with the suite green. The mutant dropping the handed grace in the except branch of `_bounded` (lanes.py:198, `_kill_group(proc, grace)` to `_kill_group(proc)`) survived `test_lane_land_brief_bound_group.py`, including the new `test_the_brief_alone_is_given_critic_s_replay_stop_grace`. It also survived `test_lane_land_commit_timeout_group.py`, `test_kill_grace_interrupt.py` and `test_critic.py -k BriefAuthorMutants`. Two Ctrl-C cases failed on the loaded first run and passed alone under the mutant, so they were load flakes, not kills. The branch is live in isolation. `_bounded(["sh", "-c", ...], 1, 8)` over a member that takes 4 s to stop on SIGTERM lets it stop cleanly at HEAD (5.0 s, its marker written). Under the mutant it is sent SIGKILL at `KILL_GRACE` (3.0 s, no marker). The grace argument of `_bounded` is non-None only for the brief, and the commit's cases cannot tell `KILL_GRACE` from the default, so only a BG1627 case can pin it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1627 AC1 still passes: Given `critic.BRIEF_TIMEOUT` shrunk below the replay's run time in a fixture, when `sprint.py lane land` runs and the bound fires, then it stops and no mutation runner or pytest child the replay started outlives the stop, and the replay's scratch copy is removed. Fails on: only critic.py is killed, so the runner and its pytest children keep running and the scratch copy stays.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_brief_bound_group.py::LandBriefBoundKillsReplayTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
