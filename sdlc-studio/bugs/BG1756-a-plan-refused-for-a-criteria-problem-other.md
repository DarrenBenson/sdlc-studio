# BG1756: A plan refused for a criteria problem other than a missing Verify line names only the Affects and Points template

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** an independent reviewer's verdict in run twenty-six (RUN-01M87B5M), recorded as non-blocking and pre-existing at the unit's base (BG0960, engineering seat, verdict c5ecc0cce808-6a36f47a)
> **Distinct-from:** BG0960
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T08:33:01Z

## Summary

BG0960 made a plan refusal for a missing Verify line name the Verify line as the fix. A unit refused for another criteria problem (for example a criterion without a Fails-on clause) still gets only the Affects and Points templates, so the refusal names no fix for what it lacks.

## Steps to Reproduce

1. A batch unit with Affects and Points whose criterion lacks a Fails-on clause.
2. `sprint plan`.
3. The refusal prints only the Affects and Points templates.

## Proposed Fix

Have `_breakdown_fix` name the repair for each `ac_why` reason the breakdown can report, not only `no-verifier`.

## Acceptance Criteria

- [ ] **AC1** Given a batch unit refused at `sprint plan` for a criteria problem other than a missing Verify line, when the refusal prints, then it names the fix for that problem. Fails on: the refusal printing only the Affects and Points templates.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
