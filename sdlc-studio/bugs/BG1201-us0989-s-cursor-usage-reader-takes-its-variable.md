# BG1201: US0989's Cursor usage reader takes its variable names and response shape from documentation, not from a real Cursor cloud run

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG1201.md
> **Evidence:** US0989 builder report, 2026-11-04, outside-the-unit items 1 and 2.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T12:17:34Z

## Summary

2026-11-04, US0989's build (run five). lib/`meter_cursor.py` calls `GET /v1/agents/{id}/usage` with `CURSOR_API_KEY` when `SDLC_STUDIO_CURSOR_AGENT_ID` is set. Cursor's cloud-agent docs name no variable carrying the agent id, so `SDLC_STUDIO_CURSOR_AGENT_ID` is the skill's own name and the operator must set it, and the key name and the `totalUsage`/`runs[]` shape come from CR0611 and a third-party copy of the API reference. US0989's Notes asked for both to be taken from a real run. A shape mismatch fails safe: the cross-check refuses the reading and the run reads NOT MEASURED.

## Steps to Reproduce

1. Start a Cursor cloud agent on a project using sdlc-studio.
2. Print its environment and call the usage endpoint for its agent id.
3. Compare with `meter_cursor.py`'s SIGNALS, key name and parsed fields.

## Proposed Fix

Confirm the names and the shape on a real Cursor cloud run, and adopt Cursor's own agent-id variable in SIGNALS if one exists.

## Acceptance Criteria

- [ ] **AC1** `meter_cursor.py`'s signal and key names and its parsed usage fields match a recorded response from a real Cursor cloud run, kept as the test's fixture.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py

## Impact

A Cursor cloud run may read NOT MEASURED until the operator sets the agent id by hand, which is the gap CR0611 exists to close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
