# BG1668: personas.standard: report does not cover the goal review's refusal of a traced persona card, which still refuses under report mode

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_persona_block.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T13:56:22Z

## Summary

Lane K's builder (RUN-01M7VNR0) found that US1322's report mode reaches only project seat cards resolved through `persona_resolve.` The goal review's refusal to brief from a traced persona card that fails the standard (US1056) does not read personas.standard, so a project set to report mode while it upgrades is still refused at goal-review brief for its own persona cards, against reference-config.md's account of report mode naming rather than refusing a project's own cards.

## Steps to Reproduce

In a fixture project set personas.standard: report, give a traced persona card a demographic token, and run sprint.py goal-review brief --seat qa: it refuses rather than naming the card and framing it.

## Proposed Fix

Have the goal review's persona-card check read personas.standard and, in report mode, name the card with its remedy and continue, as `persona_resolve` does; pin both modes in `test_goal_review_persona_block.py.`

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Lane K's builder (RUN-01M7VNR0) found that US1322's report mode reaches only project seat cards resolved through `persona_resolve.` The goal review's refusal...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a fixture project set personas.standard: report, give a traced persona card a demographic token, and run sprint.py goal-review brief --seat qa: it refuses...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have the goal review's persona-card check read personas.standard and, in report mode, name the card with its remedy and continue, as `persona_resolve` does...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
