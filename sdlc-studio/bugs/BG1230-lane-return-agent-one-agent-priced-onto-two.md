# BG1230: lane return --agent: one agent priced onto two units, stale --tokens wording, and undocumented help

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_priced_followups.py, changelog.d/BG1230.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** run six reviews, scratchpad run6/*-verdict-r*.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T15:34:11Z

## Summary

2026-11-05, US1117's reviews. One agent returned for two units books its whole transcript onto each, with no warning; with only --agent given, the warnings at sprint.py near 8526 and 8533 still name --tokens; help/sprint.md does not document --agent and its --minutes sentence is now false; `record_delegated_tokens`' docstring still says SUPPLIED; the report's Tokens row calls transcript-read totals supplied (`sprint_report.py` near 3830); mutant M3 survives; an unreadable subagents folder reads as no transcript.

## Steps to Reproduce

See the summary; each item was reproduced by its reviewer or builder.

## Proposed Fix

Warn when an agent already priced on another unit is returned again, correct the wording and docs, and add the missing pins.

## Acceptance Criteria

- [ ] **AC1** Returning one agent for a second unit warns and names the first; the --agent-only warnings do not name --tokens; help/sprint.md documents --agent; the Tokens row does not call a transcript total supplied.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced_followups.py

## Impact

The per-unit priced figures can double count, and the docs mislead.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
