# BG1444: sprint plan reports a malformed risk map as 'no component map is declared', says nothing when a unit's risk tag is outside the vocabulary, and no test pins which component the flag names when prefixes overlap

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/risk_class.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag_edges.py, changelog.d/BG1444.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of US1153, qa-seat-US1153-r1, verdict sdlc-studio/reviews/verdicts/US1153/376161701533-d64ef58c.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:10:07Z

## Summary

Run twelve's US1153 review (APPROVE, non-blocking): a malformed `risk.components` value makes `sprint plan` say 'no component map is declared' rather than naming the ignored value; a unit tagged with a class outside standard, elevated and high falls back to its Affects without a word; and when two map prefixes overlap, no test pins which component the flag names (the code picks correctly).

## Steps to Reproduce

Set `risk: high` (a scalar) or tag a unit `Risk-class: critical`, then run `sprint plan`: the first reads as no map, the second is silent.

## Proposed Fix

Name a malformed map value and an unknown tag in one line each; pin the overlapping-prefix case.

## Acceptance Criteria

- [ ] **AC1** Given a malformed risk map or a unit tag outside the vocabulary, when `sprint plan` runs, then one line names each and nothing refuses. Fails on: the no-map line for a malformed value, or silence on an unknown tag.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag_edges.py::PlanRiskEdgeTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
