# CR-0699: Builder and reviewer reasoning effort is a project setting, recorded in each run and measured against cost per point

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Related:** RFC0062, CR0700, CR0701, D0464
> **Evidence:** `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5` (effort); sdlc-studio/reports/RPT0028-sprint-report-run-01m7061x.md:24 (run nine's priced split); .claude/agents/sdlc-builder.md and .claude/agents/sdlc-reviewer.md (no model or effort in the frontmatter)
> **Date:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T04:05:34Z

## Summary

Opus 5.5's reasoning effort defaults to medium. Anthropic's Opus 5.5 prompting guide reports that medium matches or beats Opus 5 at high on coding, that low comes close at much lower cost, and that effort should be lowered before 'think less' wording is added to a prompt. Nothing here sets or records the effort a builder or reviewer runs at: the agent definitions name no model and no effort, so both take the orchestrating session's, and no run record or sprint report states it. Cost per point cannot be read against effort.

Thinking is billed as output. Run nine's output tokens cost $41.49 of its $126.64 (RPT0028), so effort is likely the largest lever on cost per point that no setting reaches today.

## Impact

Serves cost per point, the top concern (RFC0062). Builders and reviewers in this repo and in consuming projects; the default keeps today's behaviour, so nothing changes until a project sets it.

## Acceptance Criteria

- [ ] A project can set the reasoning effort for builders and for reviewers separately (default: inherit, today's behaviour), and a sprint wave dispatches each agent at the effort set
- [ ] Each run record and sprint report states the effort each builder and reviewer ran at
- [ ] A trial compares low against medium for builders, first on the bench fixtures (tools/bench) and then on one run's comparable units, reporting priced tokens per point, review rounds, rejections and the held-back suite score; the keep rule is recorded as a decision before the trial starts and the result is recorded against it
- [ ] A reviewer's effort is never set below its builder's without a recorded decision, as `routing.critic_tier` never makes the critic a smaller tier than the author

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Darren Benson (operator) | Raised |
