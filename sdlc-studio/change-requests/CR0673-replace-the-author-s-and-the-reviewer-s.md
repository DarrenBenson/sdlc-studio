# CR-0673: Replace the author's and the reviewer's hand-rolled mutation passes with one shipped runner (`mutation.py` with drop-conjunct and prose-polarity operators, plus arbitrary file, old and new edits), and have `critic.py self-check record` take its report and refuse unanswered survivors

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/templates/personas/amigos/, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RFC0062 Phase 3, first-time-right lens: finding 1; ceremony lens: finding 1 and the ceremony_sub.py role split; review-economy lens: finding 3
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:07Z

## Summary

Run six made 167 mutation-work calls and none went through mutation.py (python edit 74, sed -i 8, cp and .bak 4, other 80): builders 88 calls 1.28M, reviewers 45 calls 0.44M, repairs 29 calls 0.31M, orchestrator 5 calls 0.21M, with builders' self-check record calls another 0.29M (`ceremony_sub.py).` The probe ships unused: mutation.py:50 `FAULT_CLASSES` holds invert-guard, stub-return-null, unset-delivered-field and no-op-mapper, none of which drops one conjunct of a guard or touches the markdown a doc-pin test reads, and reference-sprint-toolchain.md:26 says 'opt-in; no gate reads it'. The self-check keeps only counts (critic.py:3021-3036), so the brief cannot say which mutants the author ran. 124 self-check rows since 2026-10-22 record FALSE 0 and 45 record survivors that still reached review, yet reviewers found vacuous pins: US1117 (critic-verdicts.md:1750, M11 and M12 each drop a conjunct and survive), US1120 (:1754, AC3's regex accepts the inverted rule) and run five's US1113, US0986 and US0990. Reviewers wrote 50 hand scaffolds (mutate.py, mut1220.py, probe.py).

## Impact

Builders and reviewers pay for hand mechanics on every unit, and a vacuous pin the hand pass missed costs a round 2 (US1120's only blocker). Consuming projects pay the same, because the lane brief tells builders to record a self-check.

## Acceptance Criteria

- [ ] `mutation.py` gains drop-conjunct (each operand of an and/or guard removed in turn) and, for a .md file in Affects that a declared test reads, flip-polarity (below and above, only and also, never and always, must and may, not removed); a fixture reports US1117's M11 and US1120's inverted rule as survivors.
- [ ] A runner entry point takes a JSON list of file, old, new and test entries, applies each in a scratch copy of the Affects, runs the named test, restores and checks byte identity, and prints one line per mutant (killed or survived, and the test's last line).
- [ ] `critic.py self-check record --mutants-from <report>` records the runner's verdicts and the full mutant list beside the counts and refuses a survivor with no answer, and the author brief prints the runner command for the unit's Verify selectors instead of asking for hand-chosen mutants.
- [ ] `critic.py brief` prints the author's recorded mutant list and the runner's replay of it, labelled as the author's, and a replayed author mutant is never counted as the reviewer's own pass.
- [ ] Before and after: on the next sprint builders make at most 3 mutation calls per unit against run six's 6.8 (88 over 13), and no round 2 has as its only blocker a vacuous pin the operators cover.

## Recommendation

Ship one runner both seats use and record its report; fix BG1169 and BG1200 first or the probe under-reports. Saving 1.72M per run. Author side 1.0M: the ceremony lens's builder figures (mutation 1.28M + record 0.29M = 1.57M), less BG1236's builder once the sweep lane removes it (x 13/14 = 1.46M), less 12 units x 2 runner calls x 20k (0.48M). Reviewer side 0.25M: ceremony's 0.44M reviewer pool x 0.63, the call share a runner removes per the review-economy lens (150 calls to 55), x 0.88 for the reviews left after the sweep lane. US1120's round 2 avoided: 0.47M at the agent share. The first-time-right lens's 3.5M rests on a regex it calls an upper bound (builders 182 calls, 3.50M) and review-economy's 0.8M on a wider probe pool, so the lower ceremony measure is carried; the orchestrator's mutation and record calls (0.68M) lie inside the orchestrator replay. The ceremony lens's proposal to drop the claims tally is not taken here; the claims-at-observable CR reshapes it. Risks: a fixed operator set misses mutants that need judgement (US1113's reordering, US0990's open mode) and the code probe does not mutate tests (critic.py:2510), so the reviewer's own mutant pass stays at the full tier and authors may add hand mutants; the runner takes arbitrary edits so it does not narrow what reviewers try.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
