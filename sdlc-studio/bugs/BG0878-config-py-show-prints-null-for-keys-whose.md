# BG0878: config.py show prints null for keys whose default lives only in a reader's code

> **Status:** In Progress
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_code_defaults.py, changelog.d/BG0878.md
> **Evidence:** US0759 QA review (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T16:04:41Z

## Summary

21 of the 42 dotted config keys the scripts read have no entry in config-defaults.yaml (`review.max_rounds`, `sprint.points_split_above`, `gate.budget_seconds`, `quality.done_requires_verified`, lessons.loop, report.enabled and others), so config.py show --key `review.max_rounds` prints null while 2 is in force, and show --sources lists no line for them.

## Steps to Reproduce

1. A project whose .config.yaml sets only coverage.unit. 2. config.py show --key `review.max_rounds` -> null (critic.py uses 2).

## Proposed Fix

Declare each code-owned default in config-defaults.yaml and have the readers take it from there, or have show report the reader's default.

## Acceptance Criteria

- [ ] **AC1** Given a project whose `.config.yaml` sets only `coverage.unit`, when `config.py show --key review.max_rounds --root <fixture>` runs, then it exits 0 and prints `2`, the cap `critic.py` enforces, and `config.py show --sources --key review.max_rounds` prints `default review.max_rounds = 2`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_code_defaults.py::ConfigCodeDefaultsTests::test_show_reports_the_value_in_force
  - **Fails-on:** HEAD exits 1 with `no key review.max_rounds` and `--sources` prints no line for it
- [ ] **AC2** Given the shipped scripts, when every dotted key they read with `config.get(root, "<key>", <literal default>)` is collected, then each has an entry in `config-defaults.yaml` whose value equals that literal default.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_config_code_defaults.py::ConfigCodeDefaultsTests::test_every_key_read_is_declared_with_its_default
  - **Fails-on:** HEAD, where keys such as `sprint.points_split_above`, `gate_budget.seconds` and `lessons.loop` have no entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: `config.py show` no longer prints null (US0969: `show --key review.max_rounds` exits 1, `no key review.max_rounds`), but the value in force, critic.py's DEFAULT_REVIEW_CEILING 2, is still reported nowhere, and `show --sources --key review` lists no `review.max_rounds` line; criteria authored, Points and Affects set |
