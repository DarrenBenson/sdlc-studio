# BG0831: The configuration reference documents keys the code does not honour: sprint.split_above, review.policy carry-forward, and review.max_rounds

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/carry_forward.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py, changelog.d/BG0831.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** soak F11/F22/F38; HEAD 7e53a438 grep: reference-config.md:263 vs sprint.py:1896; carry_forward_covers callers; `grep -rn max_rounds scripts/` finds critic.py only
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:34Z

## Summary

reference-config.md:263 documents `sprint.split_above`; sprint.py reads `sprint.points_split_above`, so the documented key does nothing. reference-config.md:217 documents `review.policy: carry-forward` as filing a REJECT's findings and shipping; its only runtime effect is being recorded on the close (`carry_forward_close_record`), and `conformance.carry_forward_covers` has no caller outside tests. templates/config-defaults.yaml:74 says `review.max_rounds` is deliberately absent because two consumers read it; today only critic.py reads it (the close-attempt consumer is gone) and reference-review.md:466 tells users to set it.

## Steps to Reproduce

Set `sprint.split_above: 5` and plan a 6-point unit: not refused. Set `review.policy: carry-forward` and record a REJECT: nothing is filed or shipped differently.

## Proposed Fix

Document `sprint.points_split_above`; retire `review.policy` (the lean loop carries at the cap for every project) with a Breaking row and a migrate strip, deleting the unused `carry_forward` helpers; rewrite the config-defaults comment to say `review.max_rounds` is the round cap and its only reader is critic.

## Acceptance Criteria

- [ ] **AC1** Given every key reference-config.md documents under sprint and review, then each is read by shipped code. Fails on: HEAD's `split_above` and review.policy rows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_every_documented_key_has_a_reader
- [ ] **AC2** Given templates/config-defaults.yaml, then no comment claims `review.max_rounds` has two consumers. Fails on: HEAD line 74
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_max_rounds_comment_names_one_reader

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
