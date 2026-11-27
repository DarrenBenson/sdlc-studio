# CR-0758: An irreversible action waits for the operator on its own, and the rest of an autonomous run keeps going

> **Status:** Proposed
> **Priority:** medium
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md
> **Date:** 2026-11-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-27T11:42:45Z

## Summary

reference-sprint.md says the run stops for exactly two things, an irreversible action (a push, a tag, a release, a deletion outside the batch) or acting outside its domain. Read literally in Claude Code, stopping means the orchestrator blocks on the question, so every independent lane stops too. In run twenty-eight (2026-11-26) a blocking question about deleting a 1.6 GB scratch folder, asked at about 19:40 while the operator was away, held the whole run for 11 hours: the queue drained at 21:24 and nothing started until the answer at 08:40. Say instead that only the irreversible action waits. The run asks without blocking (a plain message, or sprint decision defer for a unit), keeps every lane that does not depend on the answer moving, and acts on the answer when it arrives. Carry the same sentence into the agent prompt template's orchestrator rules. reference-sprint.md is over its line ceiling, inside tolerance, so the change cuts as much as it adds.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Raised |
