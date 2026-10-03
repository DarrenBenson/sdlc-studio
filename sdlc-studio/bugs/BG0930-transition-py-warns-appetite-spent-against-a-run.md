# BG0930: transition.py warns APPETITE SPENT against a run that is already signed

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_appetite_sealed_run.py, changelog.d/BG0930.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T11:45:22Z

## Summary

In sdlc-studio-web, transition.py printed an 'APPETITE SPENT' warning naming RUN-01M3PMW3, a run already signed over RPT0003, while status.py reported no run open. A sealed run has no appetite left to spend, so the warning describes a run that is over. Found by the v6.1 web grooming (D0326).

## Steps to Reproduce

1. A workspace whose last run is signed and whose appetite was exhausted. 2. transition.py set on any unit. 3. It warns APPETITE SPENT naming the signed run.

## Proposed Fix

Read the appetite only for a run that is open (not sealed), as status.py does. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a workspace whose last run is signed with its appetite spent, when transition.py set moves a unit, then no APPETITE SPENT warning is printed, and an open run with its appetite spent still prints it. Fails on: the current code, which warns against the signed run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_appetite_sealed_run.py::AppetiteSealedRunTests::test_a_signed_run_spends_no_appetite

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
