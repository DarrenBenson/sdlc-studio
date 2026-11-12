# CR-0701: A consolidation unit's builder brief can carry an ownership line scoped to its Affects, kept only if a measured trial earns it

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** M
> **Related:** RFC0062, CR0699, CR0700, D0464
> **Evidence:** `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2` ('Say who owns the code'); .claude/skills/sdlc-studio/scripts/sprint.py:2734 (lane_brief_text); .claude/agents/sdlc-builder.md (Affects-only rule); sdlc-studio/reports/RPT0028-sprint-report-run-01m7061x.md:24
> **Date:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T04:05:36Z

## Summary

Anthropic's prompting guide for Claude Fable 5.2 ('Say who owns the code') reports that the sentence 'You are the owner and long-term maintainer of this codebase, and its design is up to you.' raised consolidation of duplicated code on small coding tasks from under 10% of runs to about 75%. It also raised output tokens by about 70-80%, brought changes nobody asked for (new tests and docs, sometimes changed feature behaviour), and gave summaries that left small changes out. The guide says to leave it out where the user owns the code and wants it changed as little as possible, and that a scope rule does not cancel it: with 'No drive-by refactors' in the prompt the model still consolidated in over half of runs. It was measured on Fable 5.2, not on Opus 5.5, which builds here.

The operator's ruling (D0464) keeps the sentence out of AGENTS.md, CLAUDE.md, the agent definitions and the shipped agent-instructions template: AGENTS.md reaches every builder and reviewer, a builder stages only its Affects, and consuming projects own their code. This CR lets a unit whose job is consolidation opt in, with the line scoped to its Affects. Proposed wording: 'You own the design of the files this unit's Affects declares. Where the code you touch duplicates code in those files, merge it into one shared function. A change outside Affects is a finding to file, not an edit.'

## Impact

Builders on units that opt in, nothing else: reviewers, other units and consuming projects that do not opt in see no change. Serves cost per point by testing a quality lever before anyone pays for it everywhere: run nine's output tokens cost $41.49 of $126.64 (RPT0028), so a 70-80% output rise on every unit would add about $29-33 a run.

## Acceptance Criteria

- [ ] A story or bug can declare that it opts in; its lane brief then carries the ownership line naming its Affects, and a unit that does not opt in carries no ownership line
- [ ] No reviewer brief from critic.py brief, no agent definition, and neither AGENTS.md nor the shipped agent-instructions template carries the ownership line, and a test pins that
- [ ] The line is first measured on the bench (tools/bench) as an ownership arm beside the pipeline arm on the brownfield fixtures, reporting priced tokens, the held-back suite score and duplicated lines before and after, counted by one stated tool
- [ ] The first three opted-in sprint units are reported against comparable units of the same size: priced tokens per point, review rounds, out-of-Affects blockers raised and duplicated lines removed
- [ ] The keep-or-drop rule is recorded as a decision before the trial starts (proposed: keep only if at least two of the three units remove the duplication their criteria name and priced tokens per point rises by no more than 25%), and the result is recorded against it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Darren Benson (operator) | Raised |
