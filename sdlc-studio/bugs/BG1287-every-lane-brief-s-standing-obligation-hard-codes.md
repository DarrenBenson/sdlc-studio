# BG1287: Every lane brief's standing obligation hard-codes `main` and tells the builder to fast-forward, contradicting the same brief's 'do not commit'

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_trunk_integration.py, tools/tests/test_doc_claims.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, changelog.d/BG1287.md
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg B; repro under scratchpad rel63/legs/scratch-b/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:08:09Z

## Summary

The new standing obligation in every lane brief hard-codes `main` and tells the builder to land by 'fast-forwarding a local worktree onto `main` within the lane'. The same brief's closing commands (`_lane_builder_commands)` say 'Do not commit ... `sprint lane land` commits'. A project whose trunk is not `main` gets a wrong branch name, and every builder gets two contradictory instructions.

## Steps to Reproduce

Static: the `LANE_OBLIGATIONS` string at sprint.py:2520 next to the 'Do not commit and do not record the self-check' line in `_lane_builder_commands.` Both appear in `lane_brief_text` output.

## Proposed Fix

Phrase the obligation as 'the lane is landed by `sprint lane land` onto the root's branch: open no PR and push no branch', and drop the instruction to fast-forward and the literal `main`.

## Acceptance Criteria

- [ ] **AC1** Given any batch unit in a worktree lane, when `sprint lane brief` prints its standing obligations, then the landing obligation says the lane is landed by `sprint lane land` onto the root's branch (a unit declaring `Isolation: home` is instead committed by the orchestrator onto the root's branch), with no PR opened and no branch pushed, and no obligation holds the literal `main` or tells the builder to fast-forward. Fails on: a brief that tells the builder to fast-forward onto `main` beside its own 'Do not commit', or names `main` in a project whose trunk is called something else.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_landing_obligation_names_lane_land_and_no_branch
  - **Verified:** yes (2026-11-25)
- [ ] **AC2** Given the reworded obligation, when the brief is printed, then it still excepts a project whose `release_strategy` is `pr-required`. Fails on: the rewording dropping the exception, so a PR project's builder is told to open no PR.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_landing_obligation_keeps_the_pr_required_exception
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's SPA lane: the obligation's text is pinned by test_trunk_integration.py and mirrored in reference-agent-prompt-template.md item 5, which tools/tests/test_doc_claims.py checks |
| 2026-11-25 | orchestrator (delegate under D0545) | AC1 re-ruled after both seats' round-two remark: "any batch unit" read as every lane, but a home lane has no worktree for `sprint lane land` to land, so its obligation now names the orchestrator's commit; the criterion names the worktree lane and the home-lane exception, and its Verify is unchanged |
