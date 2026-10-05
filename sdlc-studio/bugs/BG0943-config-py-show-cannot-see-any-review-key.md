# BG0943: config.py show cannot see any review key declared after the severity_levels list

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_after_list.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T21:29:36Z

## Summary

config-defaults.yaml declares `review.line_coverage`, `review.blocking_priority` and `review.max_rounds` after the `review.severity_levels` list, but config.py show --key reports each as declared nowhere, while keys in sections with no list (epic.perspectives) read fine. Only the show command's reader drops a section's keys after a list: the library reader `config.get` already returns the declared defaults (2, False, 'high'), so no consumer's behaviour changes, but show tells the user a shipped key does not exist, against BG0878. Found while checking the v6.1.0 release.

## Steps to Reproduce

1. python3 .claude/skills/sdlc-studio/scripts/config.py show --key `review.max_rounds.` 2. 'no key `review.max_rounds` - neither config-defaults.yaml nor .config.yaml declares it', although config-defaults.yaml:75 does.

## Proposed Fix

Make show's reader keep reading a mapping's keys after a nested list, ideally by reading through the same parser `config.get` uses rather than a second one, so show sees every declared key. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given config-defaults.yaml as shipped, when config.py show --key runs for every leaf key config-defaults.yaml declares (including `review.max_rounds`, `review.line_coverage` and `review.blocking_priority`), then each prints the default `config.get` returns for it, and a key declared nowhere is still reported as undeclared. Fails on: the current reader, which drops keys after `review.severity_levels`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_after_list.py::ConfigKeysAfterListTests::test_keys_after_a_list_are_read

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
| 2026-10-05 | orchestrator | Re-groomed on the goal review (D0344): AC1 covers every shipped key, not three; the defect is confined to show, since config.get already reads the keys |
