# CR-0748: Every subagent brief the skill ships carries a persona seat, not only the builder and reviewer briefs

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/templates/automation/audit-finder.md, .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py
> **Evidence:** 2026-11-19: the orchestrator's 6.5 bug triage spawned 6 agents with a plain brief before the operator asked whether subagents get a persona.
> **Date:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T20:46:48Z

## Summary

The operator ruled on 2026-11-19 that a subagent with a persona is always better than a generic one (D0547, LL0057). The builder brief (`sprint.py lane brief`) names the engineering seat's work render and the review brief (`critic.py brief --seat`) carries the seat charter, but the other briefs the skill ships or tells an orchestrator to write carry none: the audit finder template, the backlog triage briefs, goal review, consult and research fan-outs, and the agent prompt template in reference-agent-prompt-template.md. An orchestrator following them spawns generic agents. Make each shipped brief name a seat and include its render from `persona_resolve.py resolve --seat <role> --render build|review`, and have the template refuse a brief with no seat, so the rule is gated rather than stated (LL0027).

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Raised |
