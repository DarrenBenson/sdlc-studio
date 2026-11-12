# BG1339: sprint.py lane accept has no path for a round-2 verdict given against a rejoinder brief, so the orchestrator records it by hand

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/BG1339.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M77177, 2026-11-12: BG1010, US1149, US1000 and US1147 round 2
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:18:48Z

## Summary

`lane accept` binds the verdict to the QA brief `lane land` saved in sdlc-studio/.local/briefs/<unit>-qa.txt. A reviewer answering its own REJECT is briefed with `critic.py brief --rejoinder`, a different brief and fingerprint, so the round-2 APPROVE is recorded with `critic.py record`, then `verify_ac` and transition are run by hand: the four commands lane accept exists to replace.

## Steps to Reproduce

REJECT a unit, repair and re-land it, brief the seat with --rejoinder, then try lane accept with the round-2 verdict.

## Proposed Fix

Read the brief the verdict file's BRIEF header names, or save the rejoinder brief where lane accept looks.

## Acceptance Criteria

- [ ] **AC1** Given a unit with a recorded round-1 REJECT and a round-2 verdict file its rejoinder brief named, when `sprint lane accept --unit <id> --verdict <file> --reviewer <same seat>` runs, then it records the verdict against the rejoinder brief's fingerprint and, on APPROVE, runs the criteria and moves the unit. Fails on: the verdict bound to the round-1 saved brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_round_two_verdict_records_against_its_rejoinder_brief

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
