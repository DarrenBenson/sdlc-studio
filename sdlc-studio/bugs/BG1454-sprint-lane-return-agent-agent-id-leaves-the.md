# BG1454: sprint lane return --agent agent-<id> leaves the unit unpriced, while lane land prints the builder as agent-<id>

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_return_agent_prefix.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1454.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:38:31Z

## Summary

`lane return --agent agent-a19d...` looked for agent-agent-a19d....jsonl and recorded nothing; the bare id worked. lane land prints 'priced from agent-<id>'s transcript', so the printed form is the one an operator copies.

## Steps to Reproduce

Run `sprint lane return --units X --agent agent-<id>` for a builder whose transcript is agent-<id>.jsonl: unpriced.

## Proposed Fix

Accept the id with or without its agent- prefix.

## Acceptance Criteria

- [ ] **AC1** Given a builder transcript agent-<id>.jsonl, when `lane return --agent agent-<id>` runs, then the unit is priced. Fails on: unpriced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_return_agent_prefix.py::LaneReturnAgentPrefixTests
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
