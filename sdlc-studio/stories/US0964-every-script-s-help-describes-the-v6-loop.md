# US0964: Every script's --help describes the v6 loop and no retired review step

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_help_text.py, changelog.d/US0964.md
> **Epic:** EP0267
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer, or the agent working for me, reading a script's --help to decide what to run
**I want** the help text to describe what the v6 command does
**So that** neither of us performs a ceremony v6 removed because the help still asks for it

## Acceptance Criteria

- **AC1:** Given the `--help` of every script in scripts/ and of each of its subcommands, then none names a surface from US0924's retired list, or a sign-off other than the run's signature, except to say it is retired. Fails on: HEAD's `sprint.py goal-review` ('`sprint plan --write` refuses a stated goal no seat has reviewed'), `sprint.py reopen` ('the sprint-level review a late sign-off needs'), `sprint.py batch` ('the done-gate and sign-off lanes'), `critic.py correct --boundary` ('held to the sign-off's own rule') and `mutation.py` ('Executable mutation-check gate'); and a scan of the top-level help only, which misses four of the five
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_help_text.py::HelpTextTests::test_no_help_names_a_retired_surface
- **AC2:** Given `sprint.py goal-review --help`, then it says the seats' read of the goal is advice printed with the plan and never a refusal, as `sprint.goal_review_status` behaves. Fails on: HEAD's help, which tells an operator an unreviewed goal will be refused and so invites a review step v6 made advisory
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_help_text.py::HelpTextTests::test_goal_review_help_says_advice

## Notes

- Depends on: US0924
- Measured 2026-09-27 by dumping the --help of 12 scripts and their subcommands (1,649 lines): 5 stale strings, listed in AC1. The code is right (sprint.py 9604-9609: 'an objection is advice ... never a refusal'); only the words are stale. Imports US0924's retired list rather than restating it, so it lands after US0924. Touches hub scripts (sprint.py, critic.py), so the commit runs over the 90 s budget (BG0754): give it a 10-minute timeout. Ratchet (LC-008): the test reads argparse objects in-process where it can, and replaces a hand check nobody runs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (US0964) |
