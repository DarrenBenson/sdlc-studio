# BG1764: The cost anatomy reads no reviewer recorded with its seat, so the report's reviewer row shows 0 agents and review spend lands under other

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-26T00:00:09Z

## Summary

`sprint.py lane accept --reviewer` records the reviewer as given, and 140 rows of the verdict ledger name it as `agent-<id> (<seat>)`. `cost_anatomy.agent_key` takes only a bare id, with or without its `agent-` prefix, and returns None for that form, so `agent_roles` classes none of those agents as a reviewer. Runs twenty-five and twenty-six (RPT0044, RPT0045) report 0 reviewer agents, with every reviewer counted under other (7 and 18 agents), so a reader cannot see what review costs.

## Steps to Reproduce

1. Run `python3 -c "import sys; sys.path[:0]=['.claude/skills/sdlc-studio/scripts/lib','.claude/skills/sdlc-studio/scripts']; import cost_anatomy as c; print(c.agent_key('agent-a99db4ff5609aac1b (qa)'))"` from the repository root: it prints `None`.
2. Read the Tokens by role table of RPT0045: the reviewer row has 0 agents and other has 18.

## Proposed Fix

`agent_key` reads the id before a trailing `(<seat>)` suffix (after a space), so a seat-suffixed reviewer resolves to its agent. A test covers the bare, prefixed and seat-suffixed forms, and a name that is not an agent id (a seat alone, `build lane`) still returns None.

## Acceptance Criteria

- [ ] **AC1** `cost_anatomy.agent_key` returns the agent id for `agent-<id> (<seat>)` as it does for `agent-<id>` and a bare id, `agent_roles` classes such a recorded reviewer as a reviewer, and a seat name alone still returns None
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Filed |
