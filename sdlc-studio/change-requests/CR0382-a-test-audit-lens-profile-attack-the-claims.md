# CR-0382: A test audit lens profile: attack the claims tests and comments make, which mutation cannot

> **Status:** Complete
> **Decomposed-into:** EP0101
> **Parent:** RFC0048
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-audit.md,.claude/skills/sdlc-studio/templates/automation/audit-finder.md,.claude/skills/sdlc-studio/scripts/audit.py
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

RFC0048 D4 resolved YES (option E): adopt a 'test' audit lens profile as the qualitative backstop to the shipped mutation gate (option G, D3). G is deterministic but structurally blind to prose that misdescribes what code or a test does - a mutant cannot detect a docstring that lies. Add the profile to the existing pluggable audit lens surface (project/skill/repo/code), with lenses drawn from the failure modes this project has actually produced. On demand, not a new close-time ceremony; option F (a per-unit adversarial test review at close) stays rejected because it pays for test quality in review rounds, the currency the project is shortest of.

## Impact

Every agent and operator relying on this repo's test suite as evidence. Three sprints running, the surviving MAJOR finding has been in a comment or docstring rather than in code (L-0146, L-0173). At RUN-01KY1WCR two of three MAJORs were false claims written in prose to justify the author's own code: a comment reading 'same answer as before' on a narrowed except clause that had in fact made a shipped library path raise, turning 7 blocking lanes red in any consuming project with one legacy-encoded config byte; and a hook comment reading 'the expensive lanes ran either way' when they had not, publishing a -85% budget drift that was not drift. Round 2 of the same review then killed two replacement tests that both took the wrong branch, one whose own docstring claimed 'the behaviour is the claim'. The mutation gate caught none of these and could not have. Without this lens the only thing standing between a lying docstring and the trunk is whether a reviewer happens to read it.

## Acceptance Criteria

- [ ] An audit lens profile named 'test' is selectable via --profile test alongside the existing project/skill/repo/code profiles
- [ ] The profile carries a lens asking whether a test can fail at all, by mutating the guard the test names
- [ ] The profile carries a lens asking whether a test reaches the code it claims to pin
- [ ] The profile carries a lens asking whether a test's docstring describes what it actually asserts
- [ ] The profile carries a lens asking whether a test is green for an incidental reason unrelated to the property under test
- [ ] Findings are filed or declined with a reason under the existing file-or-decline discipline; silence is not an answer
- [ ] Running the profile over this repo's own suite reproduces at least one of the three RUN-01KY1WCR prose MAJORs, proving the lens is not vacuous

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
