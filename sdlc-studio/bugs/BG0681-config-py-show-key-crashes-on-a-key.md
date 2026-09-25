# BG0681: config.py show --key crashes on a key whose value holds an unquoted YAML date, the path BG0670 left

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_show_dates.py, changelog.d/BG0681.md
> **Evidence:** Reproduced at 6fd766cc, 2026-09-15 (rc=1).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0670 gave `show` (the whole config) a json default for date and datetime values; `show --key` still calls json.dumps without it, so `config.py show --key gate_budget` on this repository's own config exits 1 with a TypeError, because `gate_budget` holds `baseline_date.`

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/config.py show --key gate_budget` on this repository.
2. It exits 1 with TypeError: Object of type date is not JSON serializable.

## Proposed Fix

Pass the same json default on the --key path; pin both a nested date under a dotted key and a scalar date key.

## Acceptance Criteria

- [ ] **AC1** Given a fixture config whose `gate_budget.baseline_date` is an unquoted YAML date, when `config.py show --key gate_budget` runs, then it exits 0 and prints JSON whose `baseline_date` is the ISO date string. Fails on: HEAD's `cmd_show`, whose `--key` branch calls `json.dumps` without `_json_default` and raises TypeError (reproduced on this repository's own config)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_show_dates.py::ConfigShowDateTests::test_a_nested_date_under_a_key_prints
- [ ] **AC2** Given the same fixture, when `config.py show --key gate_budget.baseline_date` runs, then it prints the quoted ISO date and exits 0. Fails on: a fix that converts dates only inside mappings, which leaves a scalar date key crashing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_show_dates.py::ConfigShowDateTests::test_a_scalar_date_key_prints

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: generic AC1 replaced with falsifiable criteria for Sprint 5 (reproduced at 013a46d0) |
