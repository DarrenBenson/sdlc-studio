# BG0385: Five units of RUN-01KYMJEM ship mechanisms with no caller: the goal panel, the defect judgement and BOTH ends of the bookend review are unreachable

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** critic.py caller-check --unit US0545 --root . -> caller-unnamed; the same for US0542, US0543, US0546, US0547
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

US0542 (`goal_panel`), US0543 (`judge_defects_against_goal`), US0545 and US0546 (`record_content_review` at plan and at close) and US0547 (`prediction_miss`) were built, tested and mutation-checked, and NOTHING CALLS ANY OF THEM. `grep` finds one internal use - `prediction_miss` calling `content_reviews` - and no other caller anywhere: not `sprint plan`, not `sprint close`, not the CLI, not the goal-verdict path.

The consequence for this sprint's own close: the plan-time question was answered by the PRE-EXISTING `goal-review record` (does this goal look achievable), not by the new content question US0545 specifies (will THIS content deliver it). The close-time question US0546 specifies was never asked at all, because there is no code path that asks it. The per-clause verdict recorded at close was assembled by hand rather than returned by the panel US0542 built, which is why the panel's author-exclusion never fired.

The repo's OWN check reports all five. `critic.py caller-check --unit <id>` returns `caller-unnamed` for each: "a mechanism that reaches no caller is inert however green its tests". It was never run over the batch.

## Steps to Reproduce

1. `grep -rn 'goal_panel\|judge_defects_against_goal\|record_content_review' .claude/skills/sdlc-studio/scripts/*.py` - the only hits are the definitions and one internal call.
2. `for u in US0542 US0543 US0545 US0546 US0547; do python3 .claude/skills/sdlc-studio/scripts/critic.py caller-check --unit $u --root .; done` - five findings, one per unit.

## Proposed Fix

Wire each mechanism to the command that should consume it: `sprint plan` asks the US0545 content question and refuses an unexplained partial; `sprint close` asks the US0546 question with the shortfall supplied, runs `goal_panel` for the per-clause verdict, and runs `judge_defects_against_goal` over the open defects; the close report shows both content answers side by side and reports a prediction miss. Then run `caller-check` over the batch as part of the close, so the next occurrence is caught by the tool rather than by an operator's question.

## Acceptance Criteria

- [ ] Each of the five mechanisms is reached from the command that should consume it, asserted end to end rather than by unit test.
- [ ] `sprint close` runs `caller-check` over the batch and reports any unit whose mechanism reaches no caller, so this class is caught by the close rather than after it.
- [ ] The five units' acceptance criteria name their CALLER, which is what `caller-check` asks for and what would have refused them at delivery.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
