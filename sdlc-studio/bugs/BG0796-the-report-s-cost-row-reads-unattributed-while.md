# BG0796: The report's cost row reads unattributed while the same report measures the run's tokens

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T07:29:12Z

## Summary

RPT0010's Estimates table measures 19.2M tokens from the run record (main thread plus 73 delegated agents), but the checklist's cost row reads 'not measured - no per-unit telemetry and no harness-tracked sprint total', because `_ck_cost` reads only per-unit spans and `sprint_actual_tokens`, which is set only by a hand-supplied retro.py accuracy --tokens. Two readers of one fact disagree, and the Not measured appendix states something false.

## Steps to Reproduce

`sprint_report.py` render --report RPT0010: Estimates tokens 19,225,437; Not measured: cost 'no harness-tracked sprint total'.

## Proposed Fix

Read the run's measured token total (`run_state.run_token_total`, as the Estimates section does) in `_ck_cost` and in retro accuracy, so a hand --tokens is an override, not the only source; one reader for the figure.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: RPT0010's Estimates table measures 19.2M tokens from the run record (main thread plus 73 delegated agents), but the checklist's cost row reads 'not measured -...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: `sprint_report.py` render --report RPT0010: Estimates tokens 19,225,437; Not measured: cost 'no harness-tracked sprint total'.
- [ ] **AC3** The proposed fix lands, pinned by a test: Read the run's measured token total (`run_state.run_token_total`, as the Estimates section does) in `_ck_cost` and in retro accuracy, so a hand --tokens is an...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
