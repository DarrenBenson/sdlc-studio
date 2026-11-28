# CR-0757: A subagent carries exactly one persona, and a unit's solution review is a panel with one agent per seat and its stakeholder

> **Status:** Complete
> **Decomposed-into:** EP0386
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/lessons/LL0057-give-every-subagent-a-persona-a-seated-agent-beats-a-generic-one.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Evidence:** Operator direction 2026-11-26 in run twenty-eight (RUN-01M8B7DJ): "a sub agent should represent only one persona", "spin up one sub agent per persona and they can exchange messages", "Add it to 6.5". The orchestrator's merged builder prompt (.local/run28/common-builder.md, reverted unused); the single-seat approach reviews of US1337, US1338, US1344, US1345, US1346, US1348 and BG1768.
> **Date:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** orchestrator; agent; claude-opus-5-5
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T18:10:53Z

## Summary

A brief the skill prints or tells an orchestrator to write carries exactly one identity: one amigo seat (engineering, qa or product, or a project's own seat card) or one stakeholder persona, never two merged into one agent. Where a unit needs several views, each view is its own subagent with its own brief, and the views reach the builder as recorded replies the orchestrator relays, one file per seat, so each agent keeps its own context across rounds. The solution review EP0385 ships becomes such a panel: `critic.py approach brief` prints one brief per seat (qa always, product when the unit changes a page, a default or a refusal) and one for the unit's stakeholder persona (the story's Persona field) when it changes what users meet; `critic.py approach record` records each seat's verdict separately; and a unit's approach is agreed only when every seat the panel names has recorded GO. The framing rules in reference-agent-prompt-template.md gain the one-identity rule, LL0057 says it, and a test refuses a shipped brief that names two seats.

## Impact

Every project that delegates to subagents. Today nothing stops an orchestrator merging seats into one brief, which blurs whose judgement a reply is and weakens the independence the review gate relies on; the orchestrator of run twenty-eight did exactly that and only the operator caught it. The single-seat solution review also leaves the product seat and the stakeholder out of the plan, though run twenty-eight's rejections included false upgrade sentences and over-broad refusals that are theirs to catch.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | orchestrator | Raised |
