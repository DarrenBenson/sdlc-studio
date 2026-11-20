# BG1651: The End-goal scope lint misdescribes `**` and suggests a replacement for a bare `**` that names no file

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:32:07Z

## Summary

US1039's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1039/5596c04ba4a1-09bde1a8.txt, RUN-01M7VNR0). The scope lint's message says `**` 'matches one literal segment' (lib/`persona_goals.py`:147-148, repeated in the test comment at `test_persona_goal_lines.py`:179), but `_component_names` reads `**` as an fnmatch wildcard inside one segment, so `ha/rooms/**` names `ha/rooms/bed.yaml`. `_without_globstar` turns a bare `**` into '/' (line 120), which names no file, so the lint's own suggested replacement is the silent pattern AC2 exists to name.

The qa seat (verdict `sdlc-studio/reviews/verdicts/US1039/a220d3dc3696-6a6718d4.txt`) found a third case: the leading-`**` branch of `_without_globstar` (lib/`persona_goals.py`:117-120) names a replacement still carrying `**`, so `**/rooms/**` gives "write `rooms/**`" and following the advice draws the same warning again. A mutant returning the pattern unchanged from that branch survives the test module.

## Steps to Reproduce

Run validate.py personas on a card whose End goal says 'Applies-to: **': the suggested replacement is '/', and `sprint._component_names(`'/') matches nothing.

## Proposed Fix

Describe `**` as a single-segment wildcard, and for a bare `**` suggest the directory form the card means (or name no replacement).

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1039's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1039/5596c04ba4a1-09bde1a8.txt, RUN-01M7VNR0).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run validate.py personas on a card whose End goal says 'Applies-to: **': the suggested replacement is '/', and `sprint._component_names(`'/') matches nothing.
- [ ] **AC3** The proposed fix lands, pinned by a test: Describe `**` as a single-segment wildcard, and for a bare `**` suggest the directory form the card means (or name no replacement).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
