# BG1604: sprint plan takes the stories of an untriaged inbox CR, and only the close refuses to derive the CR Complete

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG-CR-TRIAGE.md
> **Evidence:** the website's RUN-01M7R7KN, 2026-11-19: orchestrator, sprint close --dry-run
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T07:45:33Z

## Summary

A CR filed with `file_finding.py` lands in inbox. `refine` decomposed the website run's CR into an epic and five stories and `sprint plan` planned them, neither saying the CR's triage (`transition --triaged-by`) was owed. The run delivered every story, and `sprint close --dry-run` then refused: 'CR -> Complete blocked: triage requires a structured --triaged-by'. The orchestrator recorded a triage after the run (inbox -> Approved) so the close could derive the CR Complete. The bug-side twin, where `batch add` takes an inbox bug, is BG1602.

## Steps to Reproduce

File a CR with `file_finding` (inbox), refine it into an epic and stories, plan and deliver them, then run `sprint close --dry-run`: the close names the CR as not derived terminal for want of a triage, while refine and plan said nothing.

## Proposed Fix

Have `refine` (or `sprint plan`, for a batch whose units descend from an inbox request) say that the request's triage is owed and print the transition command, or refuse until it is recorded, so the gap is met at the start of the run rather than at its close.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A CR filed with `file_finding.py` lands in inbox.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: File a CR with `file_finding` (inbox), refine it into an epic and stories, plan and deliver them, then run `sprint close --dry-run`: the close names the CR as...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have `refine` (or `sprint plan`, for a batch whose units descend from an inbox request) say that the request's triage is owed and print the transition command...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
