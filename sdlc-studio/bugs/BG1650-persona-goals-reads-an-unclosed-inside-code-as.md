# BG1650: persona_goals reads an unclosed <!-- inside code as a comment that hides a card's End goals, and attaches a nested Verify to whichever goal came last

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:31:39Z

## Summary

US1039's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1039/5596c04ba4a1-09bde1a8.txt, RUN-01M7VNR0). lib/`persona_goals.py`'s comment scan runs before the fence step and ignores code spans (lines 46-70), so an unclosed <!-- in a fenced block or an inline span above End Goals swallows the rest of the card: `sprint._end_goals` returns [] where 958701b5 returned the goals. A Verify or Applies-to line nested under a later note or bullet attaches to the last numbered goal wherever it sits (lines 95-98), and a goal's second Verify silently replaces its first. None of this repository's six cards is affected.

## Steps to Reproduce

Give a card a fenced html block holding '<!--' above '## End Goals' with goals 1 and 2 below, and call `sprint._end_goals`: [] at a011a415, both goals at 958701b5. Add a 'Notes:' paragraph after goal 2 with an indented '- **Verify:** npm test': goal 2 takes that Verify.

## Proposed Fix

Track fence and code-span state before opening a comment; attach a nested line only directly under its goal's own bullet, and refuse or warn on a second Verify for one goal.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1039's engineering second seat (verdict sdlc-studio/reviews/verdicts/US1039/5596c04ba4a1-09bde1a8.txt, RUN-01M7VNR0).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Give a card a fenced html block holding '<!--' above '## End Goals' with goals 1 and 2 below, and call `sprint._end_goals`: [] at a011a415, both goals at...
- [ ] **AC3** The proposed fix lands, pinned by a test: Track fence and code-span state before opening a comment; attach a nested line only directly under its goal's own bullet, and refuse or warn on a second Verify...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
