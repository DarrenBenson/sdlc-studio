# CR-0650: The author's self-check is a step the tools run and require, not a rule an agent remembers

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-20)
> **Decomposed-into:** EP0291
> **Priority:** High
> **Type:** Process
> **Size:** M
> **Affects:** .githooks/pre-push, .claude/skills/sdlc-studio/scripts/critic.py, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py, tools/tests/test_pre_push_suite_verdict.py, changelog.d/CR0650.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, first verdict per unit: 2026-10-19 (RUN-01M59TRM) 1 of 10 APPROVE, 2026-10-13..16 9 of 19. Broken ungated rules this run: US1084's first push red on devserver1 (full suite skipped); LC-018 over-claims in US1078, BG1061, US1084, US1085 and US1086 commit messages; BG1077 filed as a load flake, then reproduced as US1076's regression; US1086 carried at the cap (BG1095) after a repair that fixed the named instances, not the class.
> **Date:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T21:02:53Z

## Summary

RUN-01M59TRM's first-review approval rate fell to 10% (1 of 10 units, against 47% the run before), and every rule broken on the author's side was an ungated one: no full suite before one push, no claim inventory before a brief, a regression filed as a flake on impression, and tests checked only against the author's own mutants. Every gated rule held. Three changes move the author's obligations into the commands the author runs. (1) The full-suite-before-a-push trigger is mechanical, not a judgement of whether a change 'touches shared surface': before sending, the pre-push hook reads `tools/run-suite.sh --check` for the tree being pushed and says when no green verdict covers it. (2) The two practices that live only in the QA seat's charter, mutating the author's tests (paraphrases, swapped clauses, a negation elsewhere in the sentence) and a claim inventory of the commit message and changelog, are printed to the author by `critic.py brief` as steps to run before the brief is handed over. (3) `critic.py brief` refuses a unit whose author has recorded no self-check (a claim inventory and a test-mutation run), as CR0520's lane-check reaches for.

## Impact

Each review round costs a rebuild, a local suite, a host push and a review: about an hour a unit this run. A self-check the author runs first turns most of those rounds into one.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Ship (2) first, since it costs one print. Then (3), the refusal. Then (1), which needs run-suite's verdict read at push time.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Raised |

## Amigo Consult

_Consulted 2026-10-20: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- CR0650 part (1), the pre-push hook naming a missing green run-suite verdict for the tree pushed: does it earn its place (LL0056) when the push gate on the gate host already runs the full suite on that commit? Left out of this breakdown pending the operator's ruling at plan approval. Answered by the operator on 2026-10-20: part (1) is retired, because the push gate is the full-suite check, and AGENTS.md's rule is reworded under US1090 (D0382).
