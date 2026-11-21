# BG1600: test_skill_metadata_neutral.py passes 'must be installed' and 'exclusive to' requirement wordings, cannot tell a fallback from its denial, and leaves four helper branches unpinned

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_skill_metadata_neutral.py, tools/tests/test_harness_neutral_docs.py, docs/why-sdlc-studio.md, changelog.d/BG1600.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1319/2f4c79618b69-47ae04d4.txt, findings 3 to 5.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:59:32Z

## Summary

US1319's qa review found by mutation: 'Claude Code must be installed.' and 'Parallel waves are exclusive to Claude Code.' pass the whole suite (the US1320 guard misses them too); a compatibility line that refuses rather than falls back, and an --agentic row that denies the fallback, pass AC1 and AC3; 'Claude Code (the default)' in the llms.txt summary passes AC2; and cutting the harness pattern, reading every llms.txt line, dropping gh CLI from `KEPT_FACTS` or disabling the 500-char limit all leave the module green. changelog.d/US1319.md's 'fails on a harness named as required in either field' over-claims accordingly.

US1320's round-one review (sdlc-studio/reviews/verdicts/US1320/1655779fbed9-73007d79.txt, finding 3) adds that tools/tests/test_harness_neutral_docs.py passes case and hyphen variants of its two named phrases, "a Claude code skill" and "a Claude Code only feature"; its repair left this because catching the spaced form in one line also flags INSTALL.md's "(Claude Code only)" scope note and adverb uses such as "Claude Code only reads".

US1320's round-two review (sdlc-studio/reviews/verdicts/US1320/140b86634149-3f94a59e.txt) adds, in the same guard: a negation in an opening phrase with no comma, or one joined by "yet", still excuses a later requirement ("Runs without a GPU yet requires Claude Code."); "needs to be installed", "have to install", "should be installed" and "Claude Code 2.x is required" pass; and REQUIREMENT_LIST refuses a neutral alphabetical harness list under a Requirements heading, which puts Claude Code first, and the must-be ending refuses "must be used with care".

BG1599's review (sdlc-studio/reviews/verdicts/BG1599/eb06f324afbd-1d9d1473.txt) adds: no test pins reference-epic.md's clean-tree waiver, the conditional step 2 checks, the "Otherwise, for each wave" branch or the safety guarantee's fallback, so each can revert with the suite green; _DENIED misses a refusal such as "stop and refuse to run the stories one at a time"; and docs/why-sdlc-studio.md still says waves run "where the harness has sub-agents (Claude Code, through its Agent tool)" with no worktree isolation, the bare condition BG1599 retired on SKILL.md and help/epic.md.

## Steps to Reproduce

Add 'Claude Code must be installed.' to SKILL.md's compatibility line in an export and run tools/tests/`test_skill_metadata_neutral.py`: it passes.

## Proposed Fix

Add must, depends on, prerequisite, exclusive and mandatory to the requirement words; refuse a denied fallback; check 'by default' in the llms.txt summary; plant a failure for each helper branch.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1319's qa review found by mutation: 'Claude Code must be installed.' and 'Parallel waves are exclusive to Claude Code.' pass the whole suite (the US1320...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Add 'Claude Code must be installed.' to SKILL.md's compatibility line in an export and run tools/tests/`test_skill_metadata_neutral.py`: it passes.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add must, depends on, prerequisite, exclusive and mandatory to the requirement words; refuse a denied fallback; check 'by default' in the llms.txt summary...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. These are gaps in this repository's metadata-neutrality tests; the shipped wording itself is correct and no user is affected. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
