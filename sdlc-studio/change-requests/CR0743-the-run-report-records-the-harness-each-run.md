# CR-0743: The run report records the harness each run ran in, beside the models it priced

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py, docs/evidence.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** sdlc-studio/reports/RPT0035.json carries no harness, runner, surface or agent_host key (checked 2026-11-18); CR0742 requested change 9.
> **Date:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T15:25:15Z

## Summary

CR0742 asks the evidence page to show the harness and model for each run, so readers can see runs outside Claude Code. The signed reports carry the models they priced but no harness field: RPT0035's JSON has no harness, runner or surface key. The token meter already knows which harness's store it read; the report should record it, and the evidence page should show it.

## Impact

Without the harness on the record, the evidence page cannot show that runs happen outside Claude Code, which is the reading CR0742 exists to correct.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

Record the harness the run meter read (and every harness when a run spans several) in the report JSON at close, render it on the report page, and add a Harness column to `sprint_report.py evidence`, reading not recorded for reports filed before the field existed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Raised |
