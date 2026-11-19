# US1192: Lane land takes several worktrees and lands them as one commit with a Refs trailer for each unit

> **Status:** Done
> **Risk-class:** high
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/US1192.md
> **Epic:** EP0326
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Lane land takes several worktrees and lands them as one commit with a Refs trailer for each unit
**So that** CR0672 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Two staged worktrees land as one commit with a Refs trailer for each unit

- **Given** two builder worktrees of one root, each holding one unit's staged change and its hand-in files
- **When** `sprint.py lane land --worktree <a> --worktree <b> --units <u1> <u2>` runs
- **Then** the root's branch gains exactly one commit holding both changes, its message carries one `Refs:` trailer per unit, the commit hooks ran once, and both worktrees and their branches are removed. Fails on: one commit per worktree, which pays the commit hook twice, or a single trailer naming only the first unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandSeveralWorktreesTests::test_two_worktrees_land_as_one_commit_with_a_refs_trailer_each
- **Verified:** yes (2026-11-19)

### AC2: Each unit keeps its own hand-in, self-check, brief and price

- **Given** the same two worktrees, each named `agent-<id>` with its own transcript and its own claims and mutants files
- **When** they are landed together
- **Then** each unit's self-check is recorded from its own worktree's files, each gets its own QA brief, each is priced from its own agent's transcript, and each hand-in is kept under `sdlc-studio/.local/lane/landed/<worktree>/`. Fails on: the second worktree's hand-in overwriting the first's, or both units priced from one transcript
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandSeveralWorktreesTests::test_each_unit_keeps_its_own_hand_in_and_price
- **Verified:** yes (2026-11-19)

### AC3: A conflict or a refused commit lands nothing and names what to resume

- **Given** two worktrees that stage different content for the same file; then two that do not conflict under a hook that refuses the commit; then one worktree named twice
- **When** `lane land` runs on each
- **Then** each exits non-zero with the root's branch where it was and every worktree still in place: the first names the conflicting file and both worktrees, the second shows the hook's refusal, the third is refused before anything moves. Fails on: a half landing, one unit on the root's branch and the other not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandSeveralWorktreesTests::test_a_conflict_or_a_refused_commit_lands_nothing
- **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
