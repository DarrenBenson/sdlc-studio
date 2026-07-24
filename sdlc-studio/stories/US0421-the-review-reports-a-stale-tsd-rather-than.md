# US0421: the review reports a STALE TSD rather than reviewing against a wrong document

> **Status:** Ready
> **Delivers:** RFC0049
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0157
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a stale TSD is reported, not reviewed against

- **Given** a TSD whose last revision predates changes to the code it describes
- **When** the strategy review runs
- **Then** it reports the TSD as STALE and names what changed since - reviewing a batch against a wrong document produces confident wrong answers, which is the class EP0071 spent a sprint repairing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StaleTsdTests::test_a_stale_tsd_is_reported_before_it_is_used

### AC2: a current TSD passes on the measurement, not on a stamp

- **Given** a TSD that is genuinely current
- **When** the check runs
- **Then** it passes, and the assertion is made against the comparison of document and code rather than against a freshness marker anyone can write
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StaleTsdTests::test_a_current_tsd_passes_on_comparison_not_on_a_marker

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
