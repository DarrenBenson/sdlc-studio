# BG1284: Dollars per point omits the coverage its dollar figure has, and the Priced cost row's reach sentence uses Claude-transcript wording for every harness

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:07:25Z

## Summary

Dollars per point divides a dollar figure that may cover only part of the priced tokens, but its basis omits the coverage the Dollar cost row states. Separately, the Priced cost row's reach sentence is Claude-transcript wording ('a subagent's transcript was not read') even when Copilot, OpenCode, Codex or Cursor metered the run.

## Steps to Reproduce

by reading.

## Proposed Fix

Append `_usd_reach(got)` to the Dollars per point basis. Phrase the Priced cost reach from `_meters_named(run_tokens)` when another harness metered the run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Dollars per point divides a dollar figure that may cover only part of the priced tokens, but its basis omits the coverage the Dollar cost row states.
- [ ] **AC2** The proposed fix lands, pinned by a test: Append `_usd_reach(got)` to the Dollars per point basis.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
