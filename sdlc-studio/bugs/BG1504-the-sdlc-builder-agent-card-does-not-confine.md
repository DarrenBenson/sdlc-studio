# BG1504: The sdlc-builder agent card does not confine a builder's clean-up to paths it created, so a builder deleted every tmp.* directory in the shared test temp directory

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/agents/sdlc-builder.md, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, changelog.d/BG1504.md
> **Evidence:** run eighteen, 2026-11-19: two parallel lane builders shared the session scratch folder, and one overwrote the other's write_mutants.py helper, leaving it crashing
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T08:20:41Z

## Summary

In run fifteen the BG1498 builder ran `rm -rf ~/.cache/sdlc-tmp/tmp.*` to clean up after a refused mktemp, although it had created nothing there. That directory is the TMPDIR every lane and the commit hook's tests share, so the same command in a parallel wave deletes another lane's live fixtures and fails its tests for no reason of its own. No other lane was running then, so nothing was lost. The builder card (templates/agents/sdlc-builder.md and its installed copy) says nothing about clean-up; the builder only learned the rule when the orchestrator told it afterwards.

## Steps to Reproduce

1. Spawn two sdlc-builder lanes in one wave.
2. Have one clean up with a glob over the shared TMPDIR.
3. The other lane's tmp.* fixtures vanish mid-test.

## Proposed Fix

Add a rule to the builder card: remove only paths you created and recorded, never a glob over a shared directory such as TMPDIR, and pin the sentence with a test that reads the card.

## Acceptance Criteria

- [ ] **AC1** Given the shipped builder card templates/agents/sdlc-builder.md, when it is read, then it tells a builder to remove only the paths it created and recorded, and never to delete by a glob over a shared directory such as TMPDIR. Fails on: a card that says nothing about clean-up, or that forbids only the one command the run met.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_the_builder_card_confines_clean_up_to_paths_the_builder_created
- [ ] **AC2** Given this repository's installed copy .claude/agents/sdlc-builder.md, when it is compared with the template, then the two carry the same clean-up rule. Fails on: the rule landing in the template while the card this repository's builders load stays silent.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_this_repository_s_copies_match_the_templates

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
