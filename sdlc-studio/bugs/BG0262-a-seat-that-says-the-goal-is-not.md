# BG0262: A seat that says the goal is NOT achievable discharges the plan gate exactly as one that says it is - the verdict's content is never read

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found on this project's FIRST live use of the Sprint Goal seat review. The engineering seat returned 'no - not at the stated appetite' with reasons, and the plan proceeded exactly as if it had said yes.

`goal_review_status` (sprint.py:1681) filters seats with `all(str(s.get(f)).strip() for f in GOAL_REVIEW_FIELDS)` where the fields are achievable, `done_means`, `one_increment.` That is a PRESENCE test. Any non-empty string passes, so 'no', 'never', 'absolutely not' and 'yes' are interchangeable. `_render_goal_review` prints `achievable=no` to the operator and then the plan writes the run.

The gate as built asks 'did a review happen', not 'what did it say'. That is a real and useful question - it is the wsjf-inputs lesson, that a stale judgement must not discharge a live gate - and the goal-pinning around it is correct. But the name and the surrounding prose read as though the verdict decides something, and it decides nothing.

Note the shape, because it is this project's own signature: the mechanism is honest, and the SENTENCES AROUND IT imply a check it does not perform. The refusal text says 'the Sprint Goal has not been reviewed by any seat', which is true; nothing anywhere says that a review saying no will not stop you.

This is the mirror image of CR0404. There, a REJECT blocks with no way to carry it forward. Here, a reject does not block at all. Both are the same missing idea: a verdict needs a defined effect, and 'recorded' is not an effect.

## Steps to Reproduce

1. Run `sprint.py goal-review record --goal "<goal>" --seat "engineering|no|<what done means>|no"`. 2. Run `sprint.py plan --worklist <file> --write --sprint-goal "<goal>"`. Observed: the plan is written and the run opened; the only trace is a printed `achievable=no`. Expected: either the plan refuses on a negative verdict, or the operator is required to record an explicit override, in the manner the engagement floor and the review legs already use.

## Proposed Fix

Give the verdict an effect. Parse `achievable` and `one_increment` against a small vocabulary rather than accepting free text - the same treatment status vocabularies already get - and refuse the plan when a seat says no, unless an override is recorded with a reason. Keep the free-text note. Do NOT settle for printing louder: a warning the operator can walk past is what exists now. If refusing is judged too strong, the minimum is that a negative verdict is stamped on the run state and quoted at the close, so the goal verdict can be judged against what the seats said before the work rather than after.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
