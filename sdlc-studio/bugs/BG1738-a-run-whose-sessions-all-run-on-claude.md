# BG1738: A run whose sessions all run on Claude and hold their subagents drops a claude -p lane run's delegated total

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** run twenty-five, lane RS repair hand-back and qa probe
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson (qa); persona; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T13:35:41Z

## Summary

When every session reading in a run includes its subagents, retro.py (`whole` at retro.py:2930) and `sprint_report.py` (near 3803) add no supplied delegated total at all. A lane run launched with `sprint lane run --harness claude` is its own `claude -p` session, in no reading, so its tokens reach the run only through its delegated record, which is then dropped: the run's Tokens figure and cost understate it. Base behaves the same. Found by the BG1204 round-one repair builder and confirmed by the qa seat's probe in run twenty-five.

## Steps to Reproduce

1. A run whose Claude session stamps include subagents. 2. A `claude -p` lane run records its delegated total through `sprint lane return`. 3. Read the run's total: the lane run's tokens are missing.

## Proposed Fix

Add a delegated record that no reading can hold (an untagged lane-run record) even when every reading includes its subagents; keep excluding in-session subagent records.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: When every session reading in a run includes its subagents, retro.py (`whole` at retro.py:2930) and `sprint_report.py` (near 3803) add no supplied delegated...
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a delegated record that no reading can hold (an untagged lane-run record) even when every reading includes its subagents; keep excluding in-session...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | Sam Eriksson (qa) | Filed |
| 2026-11-25 | sdlc-studio | Retitled: was "A Claude-only run whose sessions all hold their subagents drops a claude -p lane run's delegated total" |
