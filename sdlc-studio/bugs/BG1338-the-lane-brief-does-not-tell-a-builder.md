# BG1338: The lane brief does not tell a builder to fast-forward its worktree, and harness worktrees start at origin's commit, so builders build on a base missing the run's landed units

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py, changelog.d/BG1338.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M77177, 2026-11-12: worktrees created at 508e2408 while main was at 227ba263 and later
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:18:42Z

## Summary

Claude Code's isolated worktrees start at the remote's commit, not local main. Nothing in `sprint lane brief` says to fast-forward first, so a builder in a later wave builds on a tree without the units its own unit depends on, and every builder this run needed telling.

## Steps to Reproduce

Spawn a builder with worktree isolation in wave 2 and read its HEAD: it is origin/main, without wave 1's landed units.

## Proposed Fix

Print the fast-forward step and the expected base in the brief; lane land can check the base matched.

## Acceptance Criteria

- [ ] **AC1** Given a lane brief for a unit in an open run, when it is printed, then it tells the builder to fast-forward its worktree to local main before changing anything, and names the commit it expects. Fails on: a brief with no fast-forward step.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py::BriefHandoverTests::test_the_brief_names_the_fast_forward_to_main

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
