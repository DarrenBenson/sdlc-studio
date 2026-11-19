# BG1602: sprint batch add takes an untriaged inbox bug without saying lane accept will refuse it Fixed until it is triaged

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_batch.py, changelog.d/BG1602.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** the website's RUN-01M7R7KN, 2026-11-18: orchestrator, adding the in-run bug under the website's D0024
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T22:30:16Z

## Summary

A bug filed with `file_finding.py` lands in inbox. `sprint.py batch add` adds it to the open run and says it is held to the same gates as the rest, but not that the inbox -> triaged step (transition --triaged-by) is owed. The bug is then built and reviewed, and only `sprint lane accept` refuses to move it to Fixed: 'triage requires a structured --triaged-by'. The orchestrator then records a triage after the fact.

## Steps to Reproduce

In a project on v3 ids, file a bug with `file_finding.py` file, `sprint.py batch add <id> --reason x`, land it and run `sprint lane accept` on an APPROVE: the Fixed transition is blocked on triage.

## Proposed Fix

Have batch add refuse an inbox bug, or name the owed triage among the unit's unmet close requirements as `sprint plan` does for `verify_ac`, so it is met when the unit joins the batch.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A bug filed with `file_finding.py` lands in inbox.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a project on v3 ids, file a bug with `file_finding.py` file, `sprint.py batch add <id> --reason x`, land it and run `sprint lane accept` on an APPROVE: the...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have batch add refuse an inbox bug, or name the owed triage among the unit's unmet close requirements as `sprint plan` does for `verify_ac`, so it is met when...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
