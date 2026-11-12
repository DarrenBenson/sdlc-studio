# CR-0700: The agent instruction files and shipped templates are audited against Opus 5.5's prompting guidance, keeping every rule a gate stands behind

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Related:** RFC0062, CR0699, CR0701, D0464
> **Evidence:** `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`; `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5`; `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2` ('Keep caution from piling up', 'Review prompts and harnesses designed for earlier models'); tools/check_budgets.py:38 (AGENTS_MD_BUDGET)
> **Date:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T04:05:35Z

## Summary

The instruction text every orchestrator, builder and reviewer loads was written across several model generations. Anthropic's current guidance (the prompting best-practices page and the Opus 5.5 and Fable 5.2 guides) names patterns written for earlier models that now cost tokens or make a model too cautious: cautions that pile up (a 'never' is read as absolute), standing delegation lines, 'think less' wording where lower effort does the job, hard style limits, and stale notes. The claude-api skill ships an audit routine for exactly these files (/claude-api prompt-audit). It reports each finding with file:line, pattern, reason and confidence, proposes a diff, and keeps guardrails against current failures.

Scope: AGENTS.md, CLAUDE.md, .claude/agents/*.md, the shipped templates/agent-instructions.md and templates/agents/*, SKILL.md, the seat cards, and the text `lane_brief_text` and critic.py brief render. Deliberate rules stay and are named with their reason: no hook bypass, the worktree HOME guard, the signing rules, Affects-only staging, and the builder's 'Send no progress message unless you are blocked', which saves builder tokens nobody reads.

## Impact

AGENTS.md loads into every context, and every builder and reviewer loads its definition and brief, so a cut here pays on every call (RFC0062). Consuming projects receive the template changes through project upgrade. AGENTS.md stands at 6,580 of its 7,000-character budget.

## Acceptance Criteria

- [ ] The audit report, run with Opus 5.5 as the target model, is committed as evidence, each finding with file:line, pattern, why it is obsolete and confidence
- [ ] Each finding is dispositioned as changed, removed or kept, and each kept rule names the gate or current failure it guards
- [ ] The accepted changes land as sized stories, and the shipped template changes reach consuming projects through project upgrade
- [ ] No rule a gate enforces loses the text that tells an agent about it, and AGENTS.md stays within its budget (tools/`check_budgets.py)`
- [ ] The token size of each changed always-loaded file is reported before and after, and the next run's priced tokens per point is reported against run nine's

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Darren Benson (operator) | Raised |
