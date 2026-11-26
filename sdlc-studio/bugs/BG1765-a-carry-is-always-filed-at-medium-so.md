# BG1765: A carry is always filed at Medium, so a unit that checks a release bar barring Medium cannot close its own carry

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1765.md, sdlc-studio/.config.yaml, tools/tests/test_lean_carry_severity_bar.py
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-26T01:30:57Z

## Summary

`critic.carry_at_cap` (.claude/skills/sdlc-studio/scripts/critic.py) files every carry with a fixed `"severity": "Medium"`. In a project whose release bar bars Medium (a `known_issues` BARS row, or a decision such as an under-fifty, no-Medium bar), a unit whose own criterion checks that bar carries at the cap and its carry then fails the very criterion the unit is meant to pass: the unit cannot go Done while its carry is open at Medium, and the carry cannot close before the unit lands. Run twenty-seven hit it twice (US1331's carries BG1760 and BG1761) and broke each deadlock by re-rating the carry Low by hand under a recorded decision; no shipped tool re-rates a severity.

## Steps to Reproduce

1. In a fixture whose release bar bars Medium, carry a unit at the review cap (`critic.py record` of a REJECT at the cap).
2. Read the carry's bug file: its severity is Medium whatever the bar, and `known_issues.py bar` refuses the release while it is open.

## Proposed Fix

File the carry at the severity of the most severe blocking finding the carried verdict names, or at the highest severity the project's release bar still allows when the verdict names none; say on the carry which rule set it. A carry the operator wants higher is re-rated with a revision row as any bug is.

## Acceptance Criteria

- [ ] **AC1** Given a project whose release bar bars Medium and a unit carried at the cap whose verdict names no severity, then the carry is filed at a severity the bar allows (Low), and its bug file says which rule set it. Fails on: `critic.carry_at_cap` writes `"severity": "Medium"` whatever the bar
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CarrySeverityTests::test_a_carry_takes_a_severity_the_release_bar_allows

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Filed |
| 2026-11-26 | orchestrator | Affects adds sdlc-studio/.config.yaml and `tools/tests/test_lean_carry_severity_bar.py`: the repair sets `review.blocking_priority` to medium here and pins it in step with the release bar (D0642) |
