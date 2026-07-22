# CR-0353: the agent-instructions hygiene check verifies pointers, not that the working model is established

> **Status:** In Progress
> **Decomposed-into:** EP0097
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/agent-instructions.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`validate.check_instructions` applies six rules: AGENTS.md exists, CLAUDE.md is a thin pointer, and the text mentions the operating doctrine, LATEST.md, a release gate and the compaction re-read. All six are CROSS-REFERENCE checks. None tests that the file establishes how the project is actually developed - that delivery goes through stories and sprints, that artefacts are tool-allocated rather than hand-authored, that a story reaches Done only when its executable ACs pass, that review is independent of the author. A project can hold an AGENTS.md that passes clean while never saying work is done this way at all, and the check will report 'agent-instructions files look good'. The shipped template does carry the working model; the check does not verify any of it survived. Same shape as three defects repaired this sprint: a detector matching one form of a thing and being read as matching the thing.

## Impact

The instructions file is the mechanism that makes the discipline hold across sessions, agents and tools - it is what a fresh context reads before acting. A hygiene check that greenlights a file which omits the working model gives false assurance at exactly the point where the assurance matters most, and the failure is silent: the operator is told the file looks good.

## Acceptance Criteria

- [ ] the check verifies the working model is present, not only the pointers: delivery through stories and sprints, tool-allocated ids and index rows, executable ACs gating Done, and independent review
- [ ] each new rule names the specific missing element and the template section that supplies it, so the finding is actionable without reading the whole template
- [ ] the rules degrade honestly for a project that has deliberately scoped a practice out - a recorded opt-out is reported as such rather than as a defect
- [ ] a fixture AGENTS.md carrying every pointer but no working model FAILS the check, proving the new rules discriminate rather than restating the existing six

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
