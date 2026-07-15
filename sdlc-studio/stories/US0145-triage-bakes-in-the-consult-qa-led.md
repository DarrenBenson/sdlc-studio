# US0145: triage bakes in the consult, QA-led

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/triage.py
> **Epic:** EP0040
> **Points:** 3

## User Story

**As an** operator triaging an Issue
**I want** my questions directed at the QA-led amigo panel
**So that** reproducibility and the real-defect question are owned by QA first.

## Acceptance Criteria

### AC1: triage resolves the QA-led panel and carries it in the result

- **Given** a triage with `--question`
- **When** `triage.triage(...)` runs
- **Then** the result's `consult` is QA-led (lead = the QA seat, Sam Eriksson on the defaults)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_amigo_consult.RefineTriageConsultTests.test_triage_result_is_qa_led
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
