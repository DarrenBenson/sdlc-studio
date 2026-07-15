# CR-0276: audit must warn about workflow scale and confirm before launching a large adversarial fan-out

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-audit.md
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Operator-reported (running audit live): /sdlc-studio audit launched a large multi-agent workflow (192 agents, ~2.3M tokens, ~15 min, harness-flagged 'Large workflow') with NO warning or confirmation before the fan-out. For the adversarial superset - which can cost millions of tokens - the command should present the scoped plan and an estimated cost (agent count, token budget, wall-time) and get an explicit go-ahead BEFORE invoking the Workflow, not surprise the operator mid-run.

## Impact

Cost/safety: an operator can unknowingly trigger a multi-million-token, 15-minute-plus run. The Workflow tool flags 'Large workflow' only AFTER launch. audit should gate on a pre-flight estimate + confirmation (with a scale threshold, so a small scoped audit still runs without ceremony), and offer a bounded/quick mode.

## Acceptance Criteria

- [ ] audit presents a scope + estimated cost (agents, tokens, wall-time) before launching the fan-out
- [ ] a large run (above a threshold) requires explicit operator confirmation; a small scoped audit runs without ceremony
- [ ] reference-audit.md documents the pre-flight gate and a bounded/quick mode

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
