# BG1512: A lane builder's self-check hand-in is refused only after lane land has committed the unit, for surfaces, rulings and mutant results the brief names only in passing

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:52:04Z

## Summary

In the website's 6.4 run all three lane builders wrote hand-ins `critic.py self-check record` refuses: surfaces such as 'page:commands.mdx' or 'page prose', rulings with prose after the word ('TRUE - ...', 'TRUE in substance', 'n/a'), mutant results 'SURVIVED' and 'control-green', and a mutant killed by a build check rather than a test in Affects. `sprint lane land` commits and fast-forwards main first, then refuses the record, so the orchestrator reshaped six hand-ins by hand. A docs-only unit's own pages are also no allowed surface, though they are where its claims live.

## Steps to Reproduce

1. Have a lane builder write a claims file with surface 'page:x.mdx' or ruling 'TRUE - evidence'.
2. Run sprint.py lane land: it commits and fast-forwards main, then prints 'self-check REFUSED and no brief written'.

## Proposed Fix

Validate the hand-in before the land commits (or give the builder a `self-check check` to run), print the allowed surfaces, rulings and results in the lane brief, and accept a page in the unit's Affects as a claim surface.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In the website's 6.4 run all three lane builders wrote hand-ins `critic.py self-check record` refuses: surfaces such as 'page:commands.mdx' or 'page prose'...
- [ ] **AC2** The proposed fix lands, pinned by a test: Validate the hand-in before the land commits (or give the builder a `self-check check` to run), print the allowed surfaces, rulings and results in the lane...

## Impact

Every lane land needs hand repair of the evidence it records, which is the hand-rolling the tooling exists to remove.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
