# BG0833: The engagement floor judges a decomposed CR by its own criteria, so a CR reconcile derives Complete from planned children is refused as unplanned

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_engagement_decomposed.py, changelog.d/BG0833.md, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** followups line 64; decisions.md D0281 (2026-09-28); HEAD 7e53a438 engagement_floor._classify (~470-480)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:37Z

## Summary

`engagement_floor` classifies a unit `unplanned` when it has a multi-file footprint and no planning artefact of its own. A CR delivered wholly through its `Decomposed-into` children (each planned, each reviewed) and derived Complete by reconcile is still refused. CR0599 hit it at US0960's landing and needed waiver D0281, which says the gap was filed as a follow-up; no artefact on disk carries it. The lane blocks by default in a consuming project's gate.

## Steps to Reproduce

A CR with a two-file Affects, `Decomposed-into: US..., US...` both Done with plans, status Complete: `gate.py --only engagement-floor` fails naming the CR unplanned.

## Proposed Fix

Treat a request whose every Decomposed-into child is terminal and itself passes the floor as planned through its children.

## Acceptance Criteria

- [ ] **AC1** Given a Complete CR whose decomposed children each pass the floor, then the floor passes the CR. Fails on: HEAD, which reports it unplanned
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_engagement_decomposed.py::EngagementDecomposedTests::test_a_decomposed_request_passes_through_its_children

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
