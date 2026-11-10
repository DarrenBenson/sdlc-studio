# BG1333: A project set up before 6.3.0 never learns to integrate on trunk: project upgrade leaves its AGENTS.md without the rule, and no hygiene check notices

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py
> **Evidence:** BG1224; v6.2.0 templates/config-defaults.yaml release_strategy: pr-required; templates/agent-instructions.md:43; a consuming project's Cursor agent, 2026-11-10
> **Created:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T17:29:08Z

## Summary

SDLC Studio is designed for trunk-based delivery. BG1224 (v6.3.0) made `release_strategy: trunk` the default and wrote the rule into SKILL.md, templates/agent-instructions.md ('Integrate continuously. Commit each unit to main when its gate passes and push main; open no PR and push no branch unless `release_strategy` is pr-required.') and the lane brief. Up to v6.2.0 the default was pr-required. A project's AGENTS.md is seeded once by init, and `project_upgrade.py` does not rewrite an existing one: it reports hygiene findings from validate.py, which has no rule for the missing integration line. So a project set up on 6.2 or earlier keeps instructions with no trunk rule, and an agent that reads AGENTS.md rather than SKILL.md (Cursor) falls back to its habit of a branch and a PR per change. A consuming project's Cursor agent was found gating every unit on a PR on 2026-11-10, against the operator's intent.

## Steps to Reproduce

1. Seed a project with v6.2.0 (`init`), so its AGENTS.md has no 'Integrate continuously' line.
2. Upgrade the skill to v6.3.0 and run `project_upgrade.py`.
3. AGENTS.md is unchanged and the upgrade report names no finding about the integration rule.

## Proposed Fix

Add a hygiene rule that AGENTS.md states the integration rule matching the project's `release_strategy`, and have the upgrade report it with the exact line to add, or add it under a marked block the project owns. State `release_strategy` in `config.py show` and in the lane brief's header, so an agent on any harness sees which applies.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: SDLC Studio is designed for trunk-based delivery.
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a hygiene rule that AGENTS.md states the integration rule matching the project's `release_strategy`, and have the upgrade report it with the exact line to...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Filed |
