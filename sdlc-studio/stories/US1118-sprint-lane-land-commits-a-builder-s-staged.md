# US1118: sprint lane land commits a builder's staged lane through the hooks, lands it on main and records each unit's self-check and review brief

> **Status:** Done
> **Delivers:** CR0661
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, changelog.d/US1118.md
> **Epic:** EP0298
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** sprint lane land commits a builder's staged lane through the hooks, lands it on main and records each unit's self-check and review brief
**So that** the commit hook's minutes are paid in no agent's context and landing a lane is one command

## Acceptance Criteria

- **AC1:** Given a git fixture whose worktree branch holds a staged change and a commit message at the hand-in path `sdlc-studio/.local/lane/commit-msg.txt`, when `sprint.py lane land --worktree <path> --units <id>` runs, then it commits in the worktree through the repository's hooks with no bypass, rebases the branch onto main, fast-forwards main, and removes the worktree and its branch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_staged_lane_is_committed_rebased_and_fast_forwarded
  - **Verified:** yes (2026-11-05)
- **AC2:** Given a hook that refuses the commit, then lane land exits non-zero, prints the refusal and the worktree to resume in, and leaves main, the worktree and the staged change as they were
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_hook_refusal_leaves_main_and_the_worktree_untouched
  - **Verified:** yes (2026-11-05)
- **AC3:** Given a rebase that conflicts, then lane land aborts the rebase, exits non-zero naming the conflicting files, and leaves main as it was
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_rebase_conflict_is_aborted_and_named
  - **Verified:** yes (2026-11-05)
- **AC4:** Given each landed unit's `<unit>-claims.json` and `<unit>-mutants.json` at the hand-in path, then lane land records each unit's self-check on main and writes its QA review brief to `sdlc-studio/.local/briefs/<unit>-qa.txt`, printing one line per unit with its review tier and brief fingerprint
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_each_landed_unit_gets_its_self_check_and_brief
  - **Verified:** yes (2026-11-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | sdlc-studio | Created via `new` (deterministic) |
