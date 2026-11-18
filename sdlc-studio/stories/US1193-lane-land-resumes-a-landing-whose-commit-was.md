# US1193: Lane land resumes a landing whose commit was refused without repeating the steps already done

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_resume.py
> **Epic:** EP0326
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Lane land resumes a landing whose commit was refused without repeating the steps already done
**So that** CR0672 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A refused commit is resumed with one commit and the hand-in kept

- **Given** a builder's worktree whose `sprint.py lane land` stopped at exit 1 because the commit hook refused, and the hook then cleared
- **When** `sprint.py lane land --resume --worktree <path> --units <id>` is run
- **Then** the lane lands at exit 0 with exactly one commit for the unit on the root's branch, the hand-in copy the first attempt kept under `sdlc-studio/.local/lane/landed/<worktree>/` is read and not emptied or copied again, and the unit's self-check and QA brief are written from it. Fails on: a resume that empties the kept hand-in and so records no self-check, or one that commits a second time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_resume.py::LaneLandResumeTests::test_a_refused_commit_resumes_with_one_commit_and_the_kept_hand_in

### AC2: A landing stopped after the fast-forward is resumed without its worktree

- **Given** a landing that fast-forwarded the root's branch and removed the worktree, then exited 1 because one unit's self-check was refused, and that unit's claims file corrected in the kept hand-in
- **When** `sprint.py lane land --resume` is run for the same worktree name and units
- **Then** the refused unit's self-check is recorded and its QA brief written, a unit already briefed keeps the brief it has, the root's HEAD is the commit it was, and the exit is 0. Fails on: a refusal because the worktree no longer exists, a second commit, or a brief already written being rewritten
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_resume.py::LaneLandResumeTests::test_a_landing_stopped_after_the_fast_forward_resumes_without_its_worktree

### AC3: A resume with nothing to resume is refused and changes nothing

- **Given** a worktree name no stopped landing is recorded for, and beside it a worktree whose landing completed
- **When** `sprint.py lane land --resume` is run for each
- **Then** each exits 2 naming that there is no stopped landing to resume, with the root's branch, the kept hand-ins and the briefs as they were; a plain `lane land` of a fresh staged worktree in the same fixture still lands at exit 0. Fails on: a resume that lands or re-briefs a lane already complete, or exits 0 having done nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_resume.py::LaneLandResumeTests::test_a_resume_with_no_stopped_landing_is_refused

### AC4: Every landing leaves a land record of the steps it completed

- **Given** a landing that completes and a landing that stops at a refused commit
- **When** each `sprint.py lane land` exits
- **Then** a land record under `sdlc-studio/.local/lane/landed/` names the units, the steps completed and, once committed, the commit; the stopped landing's record names the step it stopped at, and `--resume` starts from that step. Fails on: a landing that leaves no record, so a resume has to guess which steps ran and `sprint close` cannot tell a landed unit from a hand commit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_resume.py::LaneLandResumeTests::test_each_landing_records_the_steps_it_completed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
