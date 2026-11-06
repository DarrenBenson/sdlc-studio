# CR-0674: Ship restricted-tool agent definitions for builders, reviewers and repairs and spawn every lane and review with them, carrying a hand-back contract (commands in the foreground, at most three lines, detail on disk) and the run's builder notes folded into the shipped lane brief

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md, install.sh, .claude/agents/, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-epic.md, .claude/skills/sdlc-studio/templates/personas/amigos/, .claude/skills/sdlc-studio/lessons/
> **Evidence:** RFC0062 Phase 3, agent-context lens: findings 1, 7 and 8; tool-output lens: finding 4; orchestration lens: finding 7
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:11Z

## Summary

All 36 run-six subagents were general-purpose and started at 39,181 to 40,027 tokens (mean 39,457): 18.3k of harness prompt and tool schemas shared by cache and about 21k written fresh per agent. Their 1,432 calls used Bash 1,247, Write 188, Edit 143, Read 79, SubagentHandback 40, ToolSearch 6 and Monitor 5, and no Agent, Skill, WebFetch, WebSearch or MCP call. Measured A/B in a workspace holding this repository's AGENTS.md: a general-purpose agent's first context 26,175, a lean agent with tools Bash, Read, Edit, Write and Monitor 13,486, with no skill listing (7,520 tokens for 44 skills, sdlc-studio's own entry 360) and no deferred tool list (3,429 tokens, 157 of 167 names MCP). The skill ships no agent definition and reference-epic.md:752-753 names general-purpose. Hand-backs averaged 771 tokens, carried by about 199 later orchestrator calls; nine wake-ups were an agent waiting on its own background command or a duplicate finished notice (0.34M). Builders read the hand-written BUILDER-BRIEF.md (5,829 chars) 9 times, half of it restating the lane brief's hand-in and budget, and run seven repeats the pattern. Six of the 13 cold-cache agents launched in the same second as the agent before them.

## Impact

Every subagent re-reads the block it never uses on each call: about 64k priced per agent in run six (2.29M over 36). A consuming project that spawns lanes pays the same per agent; the lean start also takes about 12.7k tokens off each of a lane's calls.

## Acceptance Criteria

- [ ] templates/agents/ ships sdlc-builder and sdlc-reviewer definitions (tools Bash, Read, Edit, Write and Monitor; no Skill, Agent, WebFetch or MCP) installed with the skill, and reference-agent-prompt-template.md, reference-sprint.md and reference-epic.md name them, keeping general-purpose as the fallback where a harness has no agent config.
- [ ] A spawned sdlc-builder's first context is at least 12k tokens smaller than a general-purpose agent spawned in the same session (run six: 39.5k), measured by the cost anatomy (US1124), which flags a subagent whose start exceeds a configured budget.
- [ ] The definitions and seat charters carry the hand-back contract (run every command in the foreground or wait for it; hand back in at most three lines: unit, outcome, hand-in path; no progress message unless blocked), pinned by a test.
- [ ] The durable traps from run six's BUILDER-BRIEF.md and run seven's builder notes are lessons the lane brief's lessons block carries, and a run needs no hand-written builder brief.
- [ ] reference-sprint.md's wave step launches the first agent of a parallel wave before the rest, so the others start on a warm shared prefix.

## Recommendation

Ship and install the two definitions, name them at every spawn, and put the hand-back contract and the builder traps where the shipped briefs carry them. Saving 1.63M per run: the agent-context lens's conservative 2.29M (12,689 tokens x 1,396 later calls x 0.1 + 11,649 x 36 x 1.25) x 0.775, the subagent spend left once the first-time-right CRs remove their units and rounds, less 0.25M for the 4 reviewer agents review batching removes and 0.13M for the about 100 mutation calls the runner removes = 1.40M; plus the hand-back cap at wave-sized contexts 0.04M (0.21M when carried by run six's 199 calls), the builder-brief fold 0.09M (0.115M x 0.775) and the first-launch order 0.10M (6 x 18,325 x 1.15, scaled). The waiting and duplicate wake-ups (0.34M) are mechanical turns the sprint-drive CR removes. Upper bound about 3.9M if the further 13k of MCP schemas in run six's environment also goes. Risks: Monitor and Write must stay (reviewers write verdict files); Codex CLI has no agent config and Copilot CLI and OpenCode have their own, so general-purpose stays the fallback; a CLI-level --tools allowlist without --strict-mcp-config inflates the start instead (113k measured), which is the refinement noted against US1126; the traps must land where a builder reads them or a repeat defect returns.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
