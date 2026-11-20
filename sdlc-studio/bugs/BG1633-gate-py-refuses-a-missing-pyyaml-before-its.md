# BG1633: gate.py refuses a missing PyYAML before its lanes run, but --suite-decision, --run-tests, --record-suite-verdict and --red-run still read config defaults silently

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, changelog.d/BG1633.md
> **Evidence:** run nineteen L5 hand-back, 2026-11-19
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T22:06:35Z

## Summary

US1298 (CR0731) makes gate.py exit 2 naming `python3 -m pip install pyyaml` when PyYAML cannot be imported, but only on the lanes route. The `--suite-decision`, `--run-tests`, `--record-suite-verdict` and `--red-run` routes read the project config through the same helpers and, without PyYAML, still fall back to defaults silently: the commit hook's test selection and the CI red-run answer can run on settings the project never chose, which is the silent-default defect CR0731 exists to remove. Found by US1298's builder in run nineteen.

## Steps to Reproduce

In an environment where `import yaml` fails, with a project config that sets a ci or test-selection key, run `gate.py --suite-decision --changed <path>`: it answers on the default instead of refusing.

## Proposed Fix

Run US1298's PyYAML check at the top of every gate.py route that reads the project config, with the same exit 2 and message.

## Acceptance Criteria

- [ ] **AC1** Given an interpreter where `import yaml` fails, when each of `gate.py --suite-decision`, `--run-tests`, `--record-suite-verdict` and `--red-run` runs, then each exits 2 before reading the project config and names `python3 -m pip install pyyaml`, as the lanes route does
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GatePyYamlEveryRouteTests::test_every_config_reading_route_refuses_without_pyyaml
  - **Verified:** yes (2026-11-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
