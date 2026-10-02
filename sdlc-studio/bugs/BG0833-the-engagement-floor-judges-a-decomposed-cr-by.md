# BG0833: The engagement floor judges a decomposed CR by its own criteria, so a CR reconcile derives Complete from planned children is refused as unplanned

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_engagement_decomposed.py, changelog.d/BG0833.md, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** followups line 64; decisions.md D0281 (2026-09-28); HEAD 7e53a438 engagement_floor._classify (~470-480)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:37Z

## Summary

> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: a fixture CR0001 (Complete, Affects a.py, b.py, `Decomposed-into: US0001, US0002`, both Done with ACs) - `engagement_floor.py check` exits 1: 'CR0001 (Complete): 2 source file(s), unplanned'.

`engagement_floor` classifies a unit `unplanned` when it has a multi-file footprint and no planning artefact of its own. A CR delivered wholly through its `Decomposed-into` children (each planned, each reviewed) and derived Complete by reconcile is still refused. CR0599 hit it at US0960's landing and needed waiver D0281, which says the gap was filed as a follow-up; no artefact on disk carries it. The lane blocks by default in a consuming project's gate.

## Steps to Reproduce

A CR with a two-file Affects, `Decomposed-into: US..., US...` both Done with plans, status Complete: `gate.py --only engagement-floor` fails naming the CR unplanned.

## Proposed Fix

Remove the false refusal at its root: `_has_planning` counts a `Decomposed-into` field as a planning artefact, since refine's decomposition is the planning pass. No child walk, no new waiver.

## Acceptance Criteria

- [ ] **AC1** Given a fixture CR0001 at Complete with a two-file Affects and `Decomposed-into: US0001, US0002` (both Done with ACs), when `engagement_floor.py --root <fixture> check` runs, then it exits 0 naming no violation; the same CR with the `Decomposed-into` line removed still exits 1 naming CR0001 `unplanned`. Fails on: HEAD, which exits 1 on the decomposed CR
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_engagement_decomposed.py::EngagementDecomposedTests::test_a_decomposed_request_passes_through_its_children
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-10-01 | backlog value pass (D0291) | Groomed: premise executed at HEAD; fix narrowed to `Decomposed-into` counting as planning; control arm added; Points 2 to 1 |
