# BG1497: Two config keys the code reads are undocumented: sprint.fresh_session is missing from reference-config.md and pricing.copilot_billing from config-defaults.yaml

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1497.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) US1170 builder hand-back, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T05:37:16Z

## Summary

Run fifteen's US1170 builder found that sprint.py reads `sprint.fresh_session` (default warn) but reference-config.md does not document it, and lib/prices.py reads `pricing.copilot_billing` but templates/config-defaults.yaml does not carry it. A project cannot find either key from the shipped documentation; the 6.4 release notes name both with the code's defaults.

## Steps to Reproduce

grep -c `fresh_session` .claude/skills/sdlc-studio/reference-config.md (0); grep -c `copilot_billing` .claude/skills/sdlc-studio/templates/config-defaults.yaml (0).

## Proposed Fix

Document `sprint.fresh_session` in reference-config.md and add `pricing.copilot_billing` to config-defaults.yaml, each with the default the code uses; extend the config-documentation test so a key the code reads must appear in both.

## Acceptance Criteria

- [ ] **AC1** Given the shipped reference-config.md, when it is searched for `sprint.fresh_session`, then the key is documented with its values and the default `sprint.py` uses (warn). Fails on: the key absent, or documented with a default the code does not use.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_fresh_session_is_documented_with_the_default_the_code_uses
  - **Verified:** yes (2026-11-25)
- [ ] **AC2** Given the shipped templates/config-defaults.yaml, when it is loaded, then `pricing.copilot_billing` is present with the value `lib/prices.py` falls back to when the key is unset. Fails on: the key absent from the defaults, or a shipped value that changes what an unconfigured project is billed as.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_copilot_billing_ships_with_the_default_the_code_uses
  - **Verified:** yes (2026-11-25)
- [ ] **AC3** Given a config key the scripts read that is missing from either reference-config.md or config-defaults.yaml, when the config-documentation test runs, then it fails naming the key and the file that lacks it; a key present in both passes. Fails on: the next undocumented key going unnoticed because the test checks only the two named here.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py::ConfigKeysReadTests::test_a_key_the_code_reads_must_be_in_the_reference_and_the_defaults
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-25 | orchestrator (delegate under D0545) | Affects widened at the builder's BLOCKED: AC3 declares `quality.require_full_sections` in config-defaults.yaml, and `test_lean_prd_refresh.py`'s section 9 check pins that key as undeclared there, so it moves to a key the defaults do not declare |
