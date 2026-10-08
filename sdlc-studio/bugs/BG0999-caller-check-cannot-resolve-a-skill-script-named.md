# BG0999: Caller-check cannot resolve a skill script named as the consumer

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG0999.md
> **Evidence:** Field report, 2026-10-07, closing RUN-01M4B28Q on sdlc-studio-lens. Two criteria named their consumer as decisions.py waive and engagement_floor.py check. Both scripts live in the skill scripts directory. The close printed those criteria as unresolved callers, because the check looks only at the consuming project's tracked tree.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:15:59Z

## Summary

A Caller line may name a command, and for a consuming project the command is often a skill script: decisions.py waive, `engagement_floor.py` check. `caller_resolves` treats a token with a dot as a path and looks for that filename in the project's tracked tree. The skill's own scripts are not files of the project, so a criterion that correctly names the skill command is reported as a caller that does not exist. The check is a report rather than a gate, and the close still completes, but the report the operator is reading says the mechanism reaches nobody.

## Steps to Reproduce

1. In a project that is not the skill repo, write a story whose Affects is a project source file and whose criterion has Caller: decisions.py waive. 2. Run the close's caller-check over that unit. 3. It reports the caller unresolved. decisions.py is present in the skill scripts directory this process loaded.

## Proposed Fix

When a path-shaped caller token is not in the project tree, resolve it against the loaded skill's scripts directory, by filename. A name that exists in neither tree still fails. Do not treat an arbitrary word as a skill command.

## Acceptance Criteria

- [ ] **AC1** A criterion whose Caller is decisions.py waive resolves when that script exists in the loaded skill and not in the project tree
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerNamedTests::test_the_named_caller_must_resolve_when_the_caller_is_a_skill_script

## Triage

- Reproduced at d02d28af: `critic.caller_resolves(index, 'decisions.py waive')` is False for a project tree that does not hold `decisions.py`, while a project file (`app.py run`) resolves. The index is the project's tracked tree only (critic.py:2890). Pre-existing.
- Severity Medium stands as filed, though the check reports rather than gates: the false 'unresolved caller' lands on the report the operator signs. Changelog fragment renamed to the unit-id convention (LL0004).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Grok 4.7 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; changelog fragment renamed to the unit id |
