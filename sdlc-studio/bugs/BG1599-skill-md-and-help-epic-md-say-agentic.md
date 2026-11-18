# BG1599: SKILL.md and help/epic.md say --agentic runs waves in parallel 'where the harness has sub-agents', an untested claim for four harnesses, and reference-epic.md has no step for the stated one-at-a-time fallback

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/help/epic.md, .claude/skills/sdlc-studio/reference-epic.md, tools/tests/test_skill_metadata_neutral.py, changelog.d/BG1599.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1319/2f4c79618b69-47ae04d4.txt, findings 1 and 2.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:59:24Z

## Summary

US1319's qa review (APPROVE, round 1) found that SKILL.md's compatibility line and help/epic.md's --agentic row say waves run in parallel where the harness has sub-agents, while docs/harnesses.md marks in-session sub-agents untested in four harnesses and reference-epic.md's agentic mode needs the Agent tool with worktree isolation: an opencode or Copilot reader is told waves run in parallel there, which CR0742's constraints rule out. The same lines state that --agentic runs the stories one at a time elsewhere, but reference-epic.md, the procedure an agent follows for epic implement --agentic, has no step for a harness without sub-agents.

## Steps to Reproduce

Read SKILL.md line 5 and help/epic.md line 243 against docs/harnesses.md lines 19-23 and 34, and reference-epic.md lines 698-760.

## Proposed Fix

Say waves run in parallel where the harness has sub-agents with worktree isolation (Claude Code, per docs/harnesses.md); add to reference-epic.md's agentic mode the branch for a harness without them: run the stories one at a time in dependency order, as plain epic implement does.

## Acceptance Criteria

### AC1: The parallel claim names worktree isolation

- **Given** SKILL.md's `compatibility` line and help/epic.md's `--agentic` row
- **When** each is read
- **Then** each says `--agentic` runs its waves in parallel where the harness has sub-agents with worktree isolation, so neither tells a reader of a harness that docs/harnesses.md marks untested that waves run in parallel there. Fails on: "where the harness has sub-agents" with no worktree isolation
- **Verify:** pytest tools/tests/test_skill_metadata_neutral.py::SkillMetadataNeutralTests::test_the_parallel_claim_names_worktree_isolation
- **Verified:** yes (2026-11-18)

### AC2: reference-epic.md gives the no-sub-agent branch

- **Given** reference-epic.md's Agentic mode, the procedure an agent follows for `epic implement --agentic`
- **When** the harness has no sub-agents with worktree isolation
- **Then** the procedure has a step telling the agent to run the stories one at a time in dependency order, as plain `epic implement` does, in the words SKILL.md and help/epic.md use. Fails on: an Agentic mode with no such step
- **Verify:** pytest tools/tests/test_skill_metadata_neutral.py::SkillMetadataNeutralTests::test_reference_epic_states_the_no_subagent_fallback
- **Verified:** yes (2026-11-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
