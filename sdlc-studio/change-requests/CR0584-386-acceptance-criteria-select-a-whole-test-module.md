# CR-0584: 386 acceptance criteria select a whole test module, so each one over-claims and costs minutes

> **Status:** Rejected
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** sdlc-studio/stories, sdlc-studio/bugs, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Measured in RUN-01M2JA6J, 2026-09-16. corpus-verify on Lint run 35072360410: job 85.6 min, of which the red-criteria pass is 84 min and the dead-stamps pass 73 s, against a 90-minute job cap (raised to 150 in that run's repair). Run 35063993893 measured 75.9 min for the same pass. The pre-push boundary gate measured 749 s, of which module-alone is 551 s. Selector census over every story and bug: 3,439 Verify lines - 2,491 pytest node selectors, 386 WHOLE-MODULE pytest selectors, 366 shell, 126 grep, 58 manual.
> **Date:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

386 of this workspace's 3,439 Verify lines name a test FILE rather than a node, and the corpus lane executes every criterion in turn: `test_sprint.py` is named by 469 criteria, `test_critic.py` by 236, `test_transition.py` by 170. Both costs land on the same defect. The cost in TIME is that one module runs many times over inside a single corpus pass, which is most of that pass's 84 minutes. The cost in TRUTH is the defect this repository's reviews find more often than any other: a criterion whose fixture is wider than its words passes for reasons unrelated to its claim, so the module going green says nothing about the criterion, and a mutant aimed at the criterion's own line can survive while the selector stays green. Narrowing a selector is therefore a quality repair that happens to be the largest available speed-up, not a performance task.

## Impact

Everyone who reads a green criterion as evidence. Today a whole-module selector means 'these tests pass', never 'this claim holds', and the corpus lane pays for the difference every week.

## Acceptance Criteria

- [ ] A census verb reports every Verify line that selects a module rather than a node, by unit and by module, with a total that the repository can watch shrink
- [ ] `verify_ac` refuses a newly written whole-module selector, naming the criterion and the narrower node, with a recorded escape for a criterion whose subject IS the module
- [ ] The five largest modules' criteria are narrowed, each to a node that dies on the criterion's own mutant, and each change carries that mutant's kill as evidence
- [ ] The corpus red pass is re-measured in CI before and after, and the figures are recorded beside the baseline rather than claimed

## Recommendation

Census the 386 by module and by unit; narrow each to the node that would die on the criterion's own mutant, taking the largest modules first (`test_sprint`, `test_critic`, `test_transition`, `test_verify_ac`, `test_gate` - 1,175 of the selections). Refuse a NEW whole-module selector at write time with a named escape for the rare criterion that genuinely judges a module (a roster, a census, an import-alone pass), and report the standing set as a shrinking number rather than deleting it silently. Re-measure the corpus pass after each tranche, so the claim that this is the dominant cost is tested rather than assumed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Raised |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - rewrite 386 whole-module Verify selectors on closed artefacts: D0259 rules such rewrites ceremony |
