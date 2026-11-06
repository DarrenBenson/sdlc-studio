# CR-0677: Budget every always-loaded instruction file by size: cut AGENTS.md to at most 7,000 chars and the consuming-project template to at most 5,000 chars, gate both and SKILL.md's token size, and recommend a project settings file that disables unused plugins for delivery sessions

> **Status:** In Progress
> **Decomposed-into:** EP0300
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** AGENTS.md, CONTRIBUTING.md, .githooks/pre-commit, tools/check_budgets.py, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/reference-sprint.md, tools/tests/test_check_budgets.py
> **Evidence:** RFC0062 Phase 3, agent-context lens: findings 3, 4 and 5
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:25Z

## Summary

AGENTS.md is 15,786 chars, 5,790 tokens measured against a floor session (6,290 with CLAUDE.md), and sits in every subagent's instructions attachment (36 of 36) and in the main thread; its own line 7 says 'Keep it short enough to be read' and no guard budgets it. Much of it (the red-main acknowledgement, the ssh keepalive, forward-porting, the push gate, soft dependencies) is operator- or orchestrator-only, while lane agents get their rules from the lane and critic briefs. The shipped templates/agent-instructions.md (10,893 chars) adds 3,974 tokens to each consuming-project session, SKILL.md (21,633 chars, 8,322 tokens) is budgeted in lines only, and the description costs 360 tokens on every call machine-wide. The main thread carries 12,638 tokens of other skills' listing entries (7,160), deferred MCP names (3,429) and MCP schemas (2,049), though run six made no MCP or Skill call, and the repository has no .claude/settings.json. Already true of the tree.

## Impact

Every call of every session in this repository re-reads AGENTS.md, and every consuming-project session re-reads the template. The plugin load is the operator's and applies to each delivery session here.

## Acceptance Criteria

- [ ] AGENTS.md is at most 7,000 chars, keeping the start-here steps, the refusals table and one line per non-negotiable rule, with the moved text reachable from a linked reference, and a pre-commit lane refuses AGENTS.md over the budget, naming its size.
- [ ] templates/agent-instructions.md is at most 5,000 chars, keeps its gate list and commands, points at reference-doctrine.md for the rest, and is pinned by a size test.
- [ ] The SKILL.md budget check also refuses a SKILL.md over a token estimate and a description over 600 chars.
- [ ] reference-sprint.md's cost section recommends a project settings file that disables the plugins and connectors a delivery session does not use, and the cost anatomy (US1124) names the main thread's start context.
- [ ] Before and after: a headless session in this repository starts at least 3,000 tokens smaller than the 34,539 measured with today's AGENTS.md and CLAUDE.md.

## Recommendation

Trim both files to their budgets, gate them, and recommend the settings file. Saving 0.85M per run in this repository: AGENTS.md 3,223 tokens a call smaller, (0.45M subagent reads + 0.145M first-call writes) x 0.775 subagent spend left = 0.46M, plus 3,223 x 243 main-thread calls x 0.1 = 0.08M (243 is the call count the orchestrator replay leaves); the plugin cut, if the operator adopts it, 12,638 x 243 x 0.1 = 0.31M on the main thread only, because the lean agent definitions already drop the listing for subagents. A consuming project saves about 0.48M a run of run six's shape from the template trim (2,150 tokens x (1,755 x 0.1 + 37 x 1.25)), which is not counted in this repository's total; the SKILL.md saving is not grounded. Risks: moved text must stay reachable at the step that needs it; the template is a consuming project's only always-loaded statement of its gates, so the cut keeps the gate list (medium risk); claude.ai connectors may not be switchable per project (not verified), and the cut is the operator's call.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
