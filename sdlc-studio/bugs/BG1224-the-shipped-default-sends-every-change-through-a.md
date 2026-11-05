# BG1224: The shipped default sends every change through a PR, and nothing an agent loads says sdlc-studio integrates continuously to main

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-code.md, .claude/skills/sdlc-studio/reference-decisions.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_trunk_integration.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, tools/tests/test_doc_claims.py, changelog.d/BG1224.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** templates/config-defaults.yaml:208; reference-code.md lines 748-770; reference-config.md lines 372-384.
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T07:46:16Z

## Summary

2026-11-05, the operator: 'Sdlc-studio is designed for continuous integration, no branches and continuous commits, this isn't clear to some agents and harnesses (Cursor was making many PRs)'. templates/config-defaults.yaml:208 ships `release_strategy`: pr-required, under which code implement and epic implement emit gh pr create (reference-code.md, Release-Strategy Branch), and even solo-dev recommends a branch for risky or multi-commit work. SKILL.md, reference-doctrine.md and templates/agent-instructions.md (the AGENTS.md that Cursor, Codex and Copilot read) never state the integration model, so a harness that follows the shipped guidance opens a PR per change.

## Steps to Reproduce

1. Install the skill in a new project and run code implement under the default config.
2. The ship step tells the agent to run gh pr create.

## Proposed Fix

Make trunk the default `release_strategy` (commit each unit to main when its gate passes, push main, no branch, no PR; solo-dev read as trunk), keep pr-required as an opt-in, and state the rule once in SKILL.md, the agent-instructions template and the lane brief's obligations.

## Acceptance Criteria

- [ ] **AC1** templates/config-defaults.yaml ships `release_strategy`: trunk, and reference-config.md's table marks trunk the default (commit each unit to main when its gate passes, push main, no branch, no PR), reads solo-dev as trunk, and labels pr-required opt-in.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trunk_integration.py::TrunkIntegrationTests::test_the_default_strategy_commits_to_main
  - **Verified:** yes (2026-11-05)
- [ ] **AC2** SKILL.md and templates/agent-instructions.md each state the integration rule once: commit each unit to main when its gate passes, and open no PR and push no branch unless `release_strategy` is pr-required.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trunk_integration.py::TrunkIntegrationTests::test_the_router_and_agent_instructions_state_trunk_integration
  - **Verified:** yes (2026-11-05)
- [ ] **AC3** sprint.py lane brief lists an obligation that the lane lands on main and opens no PR and pushes no branch, a local worktree being fast-forwarded onto main within the lane.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trunk_integration.py::TrunkIntegrationTests::test_the_lane_brief_forbids_a_pr_or_pushed_branch
  - **Verified:** yes (2026-11-05)
- [ ] **AC4** reference-code.md's ship guidance under the default carries no gh pr create and no branch step.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trunk_integration.py::TrunkIntegrationTests::test_the_default_ship_guidance_has_no_branch_or_pr
  - **Verified:** yes (2026-11-05)

## Impact

Harnesses that follow the shipped guidance open many PRs and branches, which the review and push gates were designed to replace.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
