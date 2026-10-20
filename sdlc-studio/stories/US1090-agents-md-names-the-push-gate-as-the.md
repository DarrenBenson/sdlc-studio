# US1090: AGENTS.md names the push gate as the full-suite check, retiring the separate full-suite run before a commit

> **Status:** Ready
> **Delivers:** CR0650
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** AGENTS.md, tools/tests/test_agents_md_full_suite_rule.py, changelog.d/US1090.md
> **Epic:** EP0291
> **Points:** 1
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg, pushing a change to this repository
**I want** AGENTS.md to name the push gate as the full-suite check, so that no rule asks me for a separate full-suite run the gate then repeats
**So that** a push costs the ten minutes the gate host takes, not that plus another full run beforehand

## Acceptance Criteria

- **AC1:** Given AGENTS.md's `## Non-negotiable rules` section, when the bold sentence leading each paragraph is read, then `Run the full suite before a commit that touches shared surface.` is not one of them and `The push gate is the full-suite check.` is, and the paragraph it leads names `gate.py --boundary push`, `sdlc.gateHost` and `tools/run-suite.sh all`
  - **Verify:** pytest tools/tests/test_agents_md_full_suite_rule.py::FullSuiteRuleTests::test_the_rule_names_the_push_gate

## Notes

- Serves: Rowan Achterberg, End goal 1 (a push judged in about the ten minutes a gate host takes).
- Delivers D0382's retirement of CR0650 part (1). `tools/run-suite.sh all` stays available for checking a tree before a commit; it is no longer a rule.
- AC1 must fail on: the old lead sentence kept beside the new one; the new paragraph without `gate.py --boundary push`.
- The test reads the bold lead sentences as a set from the section, never a phrase list over its prose (RETRO0135, L-0002).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | sdlc-studio | Created via `new` (deterministic) |
