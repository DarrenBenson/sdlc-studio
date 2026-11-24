# BG1650: persona_goals reads an unclosed <!-- inside code as a comment that hides a card's End goals, and attaches a nested Verify to whichever goal came last

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/reference-persona.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py, changelog.d/BG1650.md
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

- [ ] **AC1** Given a card with a fenced html block holding `<!--` above `## End Goals` with goals 1 and 2 below, when `persona_goals.end_goals` reads it, then both goals are returned; an inline code span holding `<!--` likewise hides nothing. Fails on: `end_goals` returning `[]` because the comment scan ignores fences and spans (reproduced at HEAD).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py::CommentInsideCodeTests::test_an_unclosed_comment_opener_in_code_hides_no_goal
- [ ] **AC2** Given goal 2 followed by a `Notes:` paragraph with an indented `- **Verify:** npm test`, when `end_goals` reads it, then goal 2 has no Verify and the nested line attaches to no goal. Fails on: goal 2 taking the Verify of a later note (reproduced at HEAD: `verify='npm test'`).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py::NestedLineAttachmentTests::test_a_nested_line_under_a_note_attaches_to_no_goal
- [ ] **AC3** Given a goal with two nested Verify lines, when the card is validated, then `persona-goal-verify` warns of the second, named by card and goal number, and `reference-persona.md`'s rule table says so. Fails on: the second Verify silently replacing the first (reproduced at HEAD: `verify='b'`).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_goal_lines.py::NestedLineAttachmentTests::test_a_second_verify_on_one_goal_is_a_finding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: Points 2 to 3: three defects in one reader, plus a rule-table row (RuleTableTests); all three reproduced at HEAD through `persona_goals.end_goals`; reference-persona.md added to Affects |
