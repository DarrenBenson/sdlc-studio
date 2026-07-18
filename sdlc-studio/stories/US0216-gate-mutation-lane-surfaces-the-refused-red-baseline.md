# US0216: gate mutation lane surfaces the refused/red-baseline state

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Epic:** EP0072
> **Points:** 2

## User Story

**As an** engineer reading the gate output before a commit
**I want** the mutation lane to say when the run was refused for a red baseline
**So that** I do not read a refusal as assurance my tests can fail

## Acceptance Criteria

### AC1: A refused report renders as REFUSED with its baseline state, not as 0/0 killed

- **Given** a `mutation-report.json` carrying `refused: true` and `baseline: "fail"`, whose summary is all zeros because no mutant was applied
- **When** the gate's mutation lane renders that report
- **Then** the detail names the refusal and the baseline state (`REFUSED - baseline fail`) instead of `0/0 mutations killed`, so a refusal is never readable as a clean sweep.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_gate.MutationRefusedLaneTests.test_refused_report_names_the_refusal
- **Verified:** yes (2026-07-18)

### AC2: The refusal carries the report's own remedy

- **Given** a refused report whose `remedy` names what to do (clean the tree, or fix the failing suite)
- **When** the lane renders it
- **Then** that remedy is surfaced in the detail, so the reader learns the fix from the lane rather than having to open the report.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_gate.MutationRefusedLaneTests.test_refused_report_carries_the_remedy
- **Verified:** yes (2026-07-18)

### AC3: A refused lane counts as un-met, and a clean run is unaffected

- **Given** a refused report, and separately a normal report with mutants applied
- **When** each is rendered
- **Then** the refused report yields a non-zero count (it is not silently zero-as-clean) while a normal report's count and detail are unchanged from current behaviour.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_gate.MutationRefusedLaneTests
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored |
