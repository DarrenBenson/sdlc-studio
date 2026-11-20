# BG1637: gate.py's PyYAML refusal says a config is read as defaults, and its release and json routes are unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, changelog.d/BG1633.md
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T23:50:18Z

## Summary

US1298's engineering review (verdict b0c1be40b52c-95b2ef0e, APPROVE, non-blocking, RUN-01M7TTK3) found four gaps in gate.py's PyYAML check. (1) The refusal text and `pyyaml_refusal`'s docstring (gate.py:3358-3367, RequiredPyYamlTests' docstring `test_gate.py`:5603) say that without PyYAML a .config.yaml is read as the shipped defaults; since US1297 a present config refuses instead (PyYamlRequired, exit 1). (2) AC3's selector pins only PyYAML text on stdout, so a stray stdout line on a pass survives it. (3) The release boundary, --release and --format json routes refuse first by execution but no test pins them. (4) gate.py:3353 copies `sdlc_md.PYYAML_INSTALL` instead of importing it, so the two install commands must be kept in step by hand.

US1298's qa review (verdict 4268c6b80a87-4574e5d6) found the same first, second and fourth gaps. BG1633's qa review (verdict 4c331b306948-5337ec97) adds a fifth: changelog.d/BG1633.md says only the lanes route refused before, under one warning, which fits no committed state (the base ref printed two warnings). Reword that fragment before the 6.5 cut.

## Steps to Reproduce

Read gate.py:3366-3367 and run gate.main over a fixture with a .config.yaml and yaml hidden, with `pyyaml_refusal` stubbed to None: it ends in PyYamlRequired (exit 1), not a run on the defaults. In a copy, skip the check for --boundary release: RequiredPyYamlTests and GatePyYamlEveryRouteTests stay green.

## Proposed Fix

Reword the refusal and both docstrings to say a config-reading command refuses without PyYAML, import `PYYAML_INSTALL` from `sdlc_md`, assert stdout is unchanged on a pass, and add release-boundary, --release and --format json cases to GatePyYamlEveryRouteTests.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1298's engineering review (verdict b0c1be40b52c-95b2ef0e, APPROVE, non-blocking, RUN-01M7TTK3) found four gaps in gate.py's PyYAML check.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read gate.py:3366-3367 and run gate.main over a fixture with a .config.yaml and yaml hidden, with `pyyaml_refusal` stubbed to None: it ends in PyYamlRequired...
- [ ] **AC3** The proposed fix lands, pinned by a test: Reword the refusal and both docstrings to say a config-reading command refuses without PyYAML, import `PYYAML_INSTALL` from `sdlc_md`, assert stdout is...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
