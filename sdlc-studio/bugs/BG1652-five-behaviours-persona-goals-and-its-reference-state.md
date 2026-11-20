# BG1652: Five behaviours persona_goals and its reference state have no test: a mutant of each survives

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:32:33Z

## Summary

US1039's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1039/5596c04ba4a1-09bde1a8.txt, RUN-01M7VNR0) ran mutation.py against `test_persona_goal_lines.py` and each of these survived: fenced code skipped (lib/`persona_goals.py`:68), an empty Verify warns (:133-134, stated in reference-persona.md and changelog.d/US1039.md), nothing nested under a {{...}} goal attaches above (:104), a backticked Verify is linted (:132), and `persona_cards`' `goal_verify` and `goal_applies_to` keys (sprint.py:11781-11784).

The qa seat (verdict `sdlc-studio/reviews/verdicts/US1039/a220d3dc3696-6a6718d4.txt`) found three more: the End Goals section boundary is unpinned (the mutant at lib/`persona_goals.py`:90 that never leaves End Goals once entered survives, because the AC1 fixture's Scenario holds no numbered line); the `**Verify**:` spelling that `_NESTED_RE` accepts (line 34) is unpinned; and `sprint._end_goals` (`sprint.py`:11756) has no caller left now that `persona_cards` reads `persona_goals.end_goals`.

## Steps to Reproduce

Apply any one mutant above in a copy and run tests/`test_persona_goal_lines.py`: it stays green.

## Proposed Fix

Add one test per behaviour that fails on its mutant.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1039's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1039/5596c04ba4a1-09bde1a8.txt, RUN-01M7VNR0) ran mutation.py against...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Apply any one mutant above in a copy and run tests/`test_persona_goal_lines.py`: it stays green.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add one test per behaviour that fails on its mutant.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
