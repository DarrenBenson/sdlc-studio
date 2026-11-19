# BG1270: The always-loaded instruction cuts leave their restored rules and their budget gate unpinned, and a keep-indicator description escapes the 600-char cap

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** AGENTS.md, CONTRIBUTING.md, tools/check_budgets.py, tools/tests/test_agents_md_budget.py, tools/tests/test_check_budgets.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py, changelog.d/BG1270.md
> **Evidence:** run eight (RUN-01M6RZQZ) US1129 review rounds 1 and 2 and US1130 review round 1 ([new], non-blocking), and the orchestrator's friction log (R8-F15)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:39Z

## Summary

From US1129's review rounds 1 and 2: (1) the restored sentence 'A reviewer the author controls does not satisfy this.' (`AGENTS.md:44-47`) and the corrected hooks line (`AGENTS.md:36`) are pinned by nothing: deleting the sentence, or reverting the line to 'Each hook lists its lanes', passes `test_agents_md_budget.py` and `test_check_budgets.py`, so a later cut can drop them as US1129's first cut did (LC-015). (2) Sentences the cut dropped have no home in `AGENTS.md` or `CONTRIBUTING.md`: the style rule's 'no code-span or "only quoting the rule" exception' and `tools/style-allowlist.txt`, the imperative 'Never hand-author `_index.md`', 'claims and mutants' in the self-check, 'do not skip the gate because npm is missing', 'This repo is held to it like any consuming project', 'Scope is that unit's `Affects` against the run's base ref', and the Codex, Copilot, Cursor and Gemini and `README.md` lines. (3) `skill_description` returns the block indicator itself for a `description: >+` or `|+` block (`tools/check_budgets.py:266`), so a 650-char keep-indicator description passes while the same text under `>` is refused; (4) its folded and literal block branch has no test (`if False:` passes both modules); (5) `SKILL_MD_TOKEN_BUDGET` (`tools/check_budgets.py:41`) is unpinned: 80000 passes both modules though `changelog.d/US1129.md` states 8,000 and `SKILL.md` sits about 225 tokens under it. From US1130's review round 1: (6) the template pin holds each gate by one phrase (`GATES`, `test_agent_instructions_budget.py:32-43`), so cutting the engagement floor's rule while keeping 'Opt out with `engagement_floor: judgement`', cutting the CR / RFC to Epic to Story sentence under 'No ad-hoc coding', or rewording 'The CODE leg is not optional' to 'optional' each pass, with 17 chars of headroom under the 5,000 cap.

## Steps to Reproduce

Delete the restored sentence from `AGENTS.md` and run `tools/tests/test_agents_md_budget.py` and `tools/tests/test_check_budgets.py`: green. Give a fixture `SKILL.md` a 650-char `description: >+` block and run `tools/check_budgets.py`: it passes. Set `SKILL_MD_TOKEN_BUDGET = 80000` and rerun both modules: green. Cut the engagement floor's rule sentence from `templates/agent-instructions.md`, keeping its opt-out, and run `test_agent_instructions_budget.py`: green.

## Proposed Fix

Pin each restored or load-bearing sentence by its text in the budget tests; give the dropped sentences a home in `CONTRIBUTING.md` where no gate already prints them; strip the chomping and indentation indicators before `skill_description` measures a block, with a test per block style; pin the 8,000-token budget; and make the template's gate pins hold each rule sentence, not only its heading or opt-out.

## Acceptance Criteria

- [ ] **AC1** Given `AGENTS.md` and `CONTRIBUTING.md`, when the budget test reads them, then it holds by text the sentence 'A reviewer the author controls does not satisfy this.' and the corrected hooks line, and each rule the summary's item 2 lists is stated in one of the two pages. Fails on: deleting the sentence, reverting the line to 'Each hook lists its lanes', or a listed rule with no home, each passing.
  - **Verify:** pytest tools/tests/test_agents_md_budget.py::AgentsMdBudgetTests::test_the_restored_rules_are_held_by_their_text
- [ ] **AC2** Given a `SKILL.md` whose description is a 650-char block under `>+`, `|+`, `>-` or `|`, when `tools/check_budgets.py` runs, then each is refused as the same text under `>` is, and a 600-char block of each style passes. Fails on: the block indicator itself measured as the description.
  - **Verify:** pytest tools/tests/test_check_budgets.py::AlwaysLoadedBudgetTests::test_a_block_description_is_measured_whatever_its_indicator
- [ ] **AC3** Given `tools/check_budgets.py`, when the test reads `SKILL_MD_TOKEN_BUDGET`, then it is 8,000. Fails on: the budget raised to 80,000 with both modules green.
  - **Verify:** pytest tools/tests/test_check_budgets.py::AlwaysLoadedBudgetTests::test_the_skill_md_budget_is_8000_tokens
- [ ] **AC4** Given `templates/agent-instructions.md`, when the template pin reads it, then each gate is held by its rule sentence. Fails on: cutting the engagement floor's rule while keeping its opt-out, cutting the CR or RFC to Epic to Story sentence, or rewording 'The CODE leg is not optional' to 'optional', each passing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_each_gate_is_held_by_its_rule_sentence

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
