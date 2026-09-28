# BG0820: A unit with an independent APPROVE that the loop left at Ready or In Progress is handed over as an unanswered known issue, then sealed by sign

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py, changelog.d/BG0820.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** v6.0.0-rc.1 soak F31 (website project walkthrough); code at HEAD 7e53a438 sprint.py unanswered_units (~5470-5490): awaits_signature only under is_awaiting_signoff(status)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:24:01Z

## Summary

`unanswered_units` counts a unit as awaiting only the signature when `critic.is_awaiting_signoff(status)` holds, which is Review only. The lean loop in reference-sprint.md (Plan, Build, Review, Close, Sign) never tells the operator to move a unit to Review, and help/sprint.md assumes it is there. On the website soak the story stayed Ready through build and review; the close listed `report hold [unanswered-review]: <id>: Ready - ruling unreadable ...` although review coverage was 1/1 with an APPROVE, and `sprint sign` sealed the unit anyway. Close and sign read two different bars for the same unit.

## Steps to Reproduce

Plan a one-story run, build and record an independent APPROVE without transitioning the story, close with --retro: the report holds the unit as unanswered; `sprint sign` then moves it to Done.

## Proposed Fix

Judge the awaiting-signature case by the seal's own bar (`seal_bar_unmet`) at every pre-terminal status, not only Review, so close and sign agree; and state in the loop's Build step that a unit moves to Review when its build commits green.

## Acceptance Criteria

- [ ] **AC1** Given a batch unit at Ready carrying an independent delivery APPROVE, when the close lists unanswered units, then the unit is reported as awaiting the signature and not as unanswered. Fails on: HEAD, where only a Review-status unit can await the signature
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py::AwaitingSignatureStatusTests::test_an_approved_ready_unit_awaits_the_signature
- [ ] **AC2** Given reference-sprint.md's loop, then the Build step names the transition to Review. Fails on: the rc.1 and HEAD wording, which never moves a unit to Review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py::AwaitingSignatureStatusTests::test_the_loop_moves_a_built_unit_to_review

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
