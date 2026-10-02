# BG0831: The configuration reference documents keys the code does not honour: sprint.split_above, review.policy carry-forward, and review.max_rounds

> **Status:** Fixed
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: with `sprint: {split_above: 5}` in .config.yaml, `sprint.points_split_above()` returns 8; `carry_forward_covers`, `carry_forward_close_record`, `reject_carries_forward` and `validate_carried` have no caller outside tests and re-exports, so `review.policy` changes nothing; only critic.py reads `review.max_rounds`. Resized 2 -> 3: the retirement is a deletion of carry_forward.py and its re-exports
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/carry_forward.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/surface.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_surface.py, changelog.d/BG0831.md
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

Document `sprint.points_split_above`; retire `review.policy` (the lean loop carries at the cap for every project) by adding it to `RETIRED_CONFIG_KEYS`, which migrate already strips, and deleting `carry_forward.py`, `conformance.carry_forward_covers`, `sprint.carry_forward_close_record` and critic's re-exports; rewrite the config-defaults comment to say `review.max_rounds` is the round cap and its only reader is critic.

## Acceptance Criteria

- [ ] **AC1** Given a fixture whose `.config.yaml` sets `sprint.points_split_above: 5`, when `sprint.py plan` is given an 8-point unit (on the points scale and over 5), then it is refused as over the split threshold while a 5-point unit plans, and reference-config.md documents `sprint.points_split_above` with no `sprint.split_above` row. Fails on: HEAD's reference-config.md:263 documenting `sprint.split_above`, a key `points_split_above()` never reads (it returns 8 with `split_above: 5` set)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_the_documented_split_key_is_the_one_read
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given a fixture whose `.config.yaml` sets `review.policy: carry-forward`, when `migrate.py --apply --root <fixture>` runs, then the key is removed as retired (it is in `sdlc_md.RETIRED_CONFIG_KEYS`), `carry_forward.py` no longer ships, and no reference-*.md, help/ page or config-defaults.yaml documents `review.policy`. Fails on: HEAD, which keeps the key, ships `carry_forward.py` with no caller outside tests, and documents `carry-forward` as filing findings and shipping
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_review_policy_is_retired_not_documented
  - **Verified:** yes (2026-10-01)
- [ ] **AC3** Given templates/config-defaults.yaml, when it is read, then its `review.max_rounds` comment names critic.py's review-round cap as the only reader and no longer says two consumers read it. Fails on: HEAD line 74's two-consumer comment
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_max_rounds_comment_names_one_reader
  - **Verified:** yes (2026-10-01)

## Notes

Retiring `review.policy` collides with two Ready examples: US0759 AC1 uses `review.policy` as its `default`-sourced key and US0969 AC1 uses `config.py show --key review.policy` as the present-key control. Whichever lands second swaps the example for a key that stays (e.g. `review.blocking_priority`).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
