# BG1258: US1130 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py (new), changelog.d/US1130.md
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:02:40Z

## Summary

US1130 was rejected at round 2, the review cap, by qa-seat-US1130-r1, so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the unit's changelog fragment still lists temp-file naming among the habits the template shed (changelog.d/US1130.md:6-8, "the working habits it shed (index conventions, fan-out, foundation-first, temp-file naming, the release-notice opt-out) are in reference-doctrine.md#working-habits"), which is false since 71120f12 put the rule back at templates/agent-instructions.md:89, and the Working habits intro saying the starter points at these habits "rather than carries" them (reference-doctrine.md:277-278) is now false for item 8: the release note tells a consuming project that the BG0280 rule left its AGENTS.md, which is the round-1 regression this repair closed [LC-018]; [new] the restored rule carries no regression pin: deleting templates/agent-instructions.md:89 leaves test\_agent\_instructions\_budget, test\_init, test\_trunk\_integration, test\_lean\_cr\_filing, test\_lean\_guided\_stage\_confirm and test\_lean\_migrate\_config green, and test\_validate's one failure under that mutant is its workspace open-questions scan (OpenQuestionsTests), which does not read the template, so a later trim under a cap with 17 chars of headroom (4,983 of 5,000) can drop the rule exactly as US1130 did, with the suite still green

## Steps to Reproduce

1. Read the round 2 REJECT of US1130 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1130 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the unit's changelog fragment still lists temp-file naming among the habits the template shed (changelog.d/US1130.md:6-8, "the working habits it shed (index conventions, fan-out, foundation-first, temp-file naming, the release-notice opt-out) are in reference-doctrine.md#working-habits"), which is false since 71120f12 put the rule back at templates/agent-instructions.md:89, and the Working habits intro saying the starter points at these habits "rather than carries" them (reference-doctrine.md:277-278) is now false for item 8: the release note tells a consuming project that the BG0280 rule left its AGENTS.md, which is the round-1 regression this repair closed [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] the restored rule carries no regression pin: deleting templates/agent-instructions.md:89 leaves test\_agent\_instructions\_budget, test\_init, test\_trunk\_integration, test\_lean\_cr\_filing, test\_lean\_guided\_stage\_confirm and test\_lean\_migrate\_config green, and test\_validate's one failure under that mutant is its workspace open-questions scan (OpenQuestionsTests), which does not read the template, so a later trim under a cap with 17 chars of headroom (4,983 of 5,000) can drop the rule exactly as US1130 did, with the suite still green
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** US1130 AC1 still passes: Given `templates/agent-instructions.md`, then it is at most 5,000 chars (from 10,893), keeps its `## Operating doctrine` and `## Non-negotiable gates` sections with the gate list and commands, and points at `reference-doctrine.md` for the text it moves. Fails on: a size cap above 5,000, or a cut that drops a gate from the list.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_the_template_fits_and_keeps_its_gates
  - **Verified:** yes (2026-11-06)
- [ ] **AC4** US1130 AC2 still passes: Given the trimmed template, then the lines tests read survive: the `agent-instructions.md#operating-doctrine` anchor (`test_status.py`), the trunk-integration rule stated on one line with its commit clause, its `pr-required` opt-in and the words push `main` (`test_trunk_integration.py`), the CR-sizing claim (`test_lean_cr_filing.py`), and `test_init.py`, `test_validate.py`, `test_lean_guided_stage_confirm.py`, `test_lean_migrate_config.py` and `tools/tests/test_check_neutrality.py` pass unedited; a project initialised from it passes `validate`. Fails on: the trunk rule line or the doctrine heading cut.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_an_initialised_project_s_agents_md_still_validates
  - **Verified:** yes (2026-11-06)
- [ ] **AC5** US1130 AC3 still passes: Given `reference-sprint.md#cost-anatomy`, then it recommends a project `.claude/settings.json` that disables the plugins and connectors a delivery session does not use, and says claude.ai connectors may not be switchable per project. Fails on: the recommendation absent or stated as already enforced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_reference_sprint_recommends_the_settings_file
  - **Verified:** yes (2026-11-06)
- [ ] **AC6** US1130 AC4 still passes: Given a session transcript whose first main-thread call carries a known input and cache, when `sprint.py cost --anatomy` renders, then its header names the main thread's start context as that first call's input plus cache. Fails on: the header omitting it, or reading the largest call's context instead of the first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_main_thread_start_context_is_named
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Filed |
