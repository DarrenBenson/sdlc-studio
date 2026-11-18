# BG1598: README install table labels the GitHub Copilot row 'Copilot' because test_install_copilot_global.py pins that exact label, so the README and docs/harnesses.md name the harness differently

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_install_copilot_global.py, README.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py
> **Evidence:** US1318 builder hand-back, 2026-11-18; sdlc-studio/reviews/verdicts/US1321/19ef1a51a344-e3f271af.txt.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:45:07Z

## Summary

US1318's builder kept the README install row as '| Copilot |' because tools/tests/`test_install_copilot_global.py` (outside the unit's Affects) requires that exact row text; docs/harnesses.md and CR0742 call the harness GitHub Copilot. Also from US1321's round-two review: no test pins the NOT MEASURED skip in `sprint_report.py`'s `_NO_MODEL` (a mutant dropping it survives), though no shipped report carries that value.

## Steps to Reproduce

Rename the README row to '| GitHub Copilot |' and run tools/tests/`test_install_copilot_global.py`: it fails on the label alone.

## Proposed Fix

Have the test match the row by its install target or a label set, then relabel the README row GitHub Copilot; add a fixture whose Cost model figure reads NOT MEASURED.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1318's builder kept the README install row as '| Copilot |' because tools/tests/`test_install_copilot_global.py` (outside the unit's Affects) requires that...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Rename the README row to '| GitHub Copilot |' and run tools/tests/`test_install_copilot_global.py`: it fails on the label alone.
- [ ] **AC3** The proposed fix lands, pinned by a test: Have the test match the row by its install target or a label set, then relabel the README row GitHub Copilot; add a fixture whose Cost model figure reads NOT...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
