# BG0884: US0971 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Closed with findings in:** US0971's discharge: its rejecting reviewer's APPROVE answered every finding (RUN-01M3VF2J critic-verdicts)
> **Discharge review 1:** REJECT by the rejecting reviewer (2026-10-01): a782e2e8 scrubbed every GIT_* variable, dropping GIT_CONFIG_GLOBAL/SYSTEM so the AC2 Verify reads the host's global git config - fix: reuse verify_ac._REPO_LOCATING_GIT_VARS
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/blocker_sweep.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py, changelog.d/US0971.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_blocker_sweep.py
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T18:37:22Z

## Summary

US0971 was rejected at round 2, the review cap, by qa-seat reviewer (subagent aa5c57b5), so it was carried as a known issue rather than reviewed again. The findings still open: [regression] MOVED: installed hooks still go silent in two cases - \_hook\_installed (sprint.py:11752) checks the four HOOK\_PATHS relative to the root plus the core.hooksPath value as a plain string, missing (a) a linked git worktree, where .git is a file and the hooks sit in the common dir, and (b) a ~-prefixed core.hooksPath, which git expands - so sprint.py:11955 suppresses the warning where base reported UNRECONCILED - repro (a): executable .git/hooks/pre-commit running pytest, git worktree add ../wt, sprint.py plan --root ../wt - fix: resolve with git rev-parse --git-path hooks; [pre-existing] non-blocking: a husky hook that agrees with the policy reports UNRECONCILED because hook\_per\_commit\_mode never reads core.hooksPath, same at base

## Steps to Reproduce

1. Read the round 2 REJECT of US0971 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0971 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [regression] MOVED: installed hooks still go silent in two cases - \_hook\_installed (sprint.py:11752) checks the four HOOK\_PATHS relative to the root plus the core.hooksPath value as a plain string, missing (a) a linked git worktree, where .git is a file and the hooks sit in the common dir, and (b) a ~-prefixed core.hooksPath, which git expands - so sprint.py:11955 suppresses the warning where base reported UNRECONCILED - repro (a): executable .git/hooks/pre-commit running pytest, git worktree add ../wt, sprint.py plan --root ../wt - fix: resolve with git rev-parse --git-path hooks
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] non-blocking: a husky hook that agrees with the policy reports UNRECONCILED because hook\_per\_commit\_mode never reads core.hooksPath, same at base
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** US0971 AC1 still passes: Given a project after `init.py run` with no `sdlc-studio/personas/seats/`, when `sprint.py plan --goal <text>` runs, then it does not print `no seat can review it` and names the shipped seats that would review the goal. Fails on: HEAD prints `goal review: UNREVIEWED - this project declares no review seats of its own`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_a_fresh_project_is_offered_the_shipped_seats
  - **Verified:** yes (2026-10-01)
- [ ] **AC4** US0971 AC2 still passes: Given a project after `init.py guided --skip` of the TSD stage and with no commit hook installed, when `sprint.py plan` runs, then it prints neither `test strategy: UNAVAILABLE` nor `execution policy DIVERGES`. Fails on: HEAD prints both on that project's first plan
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_init_chosen_states_are_not_reported_as_divergence
  - **Verified:** yes (2026-10-01)
- [ ] **AC5** US0971 AC3 still passes: Given a Superseded story carrying `Blocked by:` a Done story, beside a Blocked story with the same blocker, when `sprint.py plan` runs its blocker sweep, then only the Blocked story is proposed. Fails on: HEAD proposes the terminal unit (premise: 14 terminal units here)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_the_blocker_sweep_skips_terminal_units
  - **Verified:** yes (2026-10-01)
- [ ] **AC6** US0971 AC4 still passes: Given engineering judged a goal NOT achievable and the goal was amended with `sprint.py goal-review record --amend-from <prior> --requesting-seat engineering`, when `sprint.py plan --write` runs, then it prints no `judged the goal NOT achievable` advice from engineering. Fails on: HEAD carries engineering's verdict forward onto its own wording
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_the_requesting_seats_verdict_is_discharged_by_its_amendment
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
