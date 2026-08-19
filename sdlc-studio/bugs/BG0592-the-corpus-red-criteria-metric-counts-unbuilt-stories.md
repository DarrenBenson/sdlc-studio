# BG0592: the corpus red-criteria metric counts unbuilt stories, which is why its number has never been stable

> **Status:** Open
> **Severity:** High
> **Verification depth:** functional (fifteen criteria drive the real release lane over temp corpora at seven story statuses. AC15 drives it through the SHIPPED CLI by subprocess and is the only one that does - a review found this field claiming 'several through the shipped CLI' when every `Verify:` line resolved to a class whose entry point is `gate.run_gate(...)`, so the coverage the sentence described has been ADDED rather than the sentence softened. Mutation: 18 declared Test Plan rows across the 15 criteria - AC13 carries four, because subtracting a subset, counting manual criteria as green, and emitting the clause unconditionally are distinct ways for it to be wrong. `run --from-plan` joins one row per criterion, so it reports 15 of the 18: `verify_ac._testplan_rows` keys by criterion and silently drops the extras, which is the enumerated-list shape this repository keeps meeting and is filed separately. Every row was executed. Each anchor asserted unique, `__pycache__` purged and `python3 -B`, all 18 KILLED, restore byte-exact - TEN of them from three review rounds that rejected the first, second and third cuts, including one that reverted the entire repair in a single line while every test stayed green. Re-measured end to end through `verify-corpus.sh` in an isolated worktree: 20 red on Done of 87 in total, with the 67 excluded rows printed in full with their statuses. THREE false readings were taken and discarded before the baseline moved - 26, inflated by the author's own uncommitted style violation breaking a lane six criteria invoke; a per-AC 21 whose extra row was a load timeout; and an 88/68/21 partition carried into durable prose after the measurement had already corrected it to 87/67/20. This field itself carried a fourth such error, claiming ten criteria and thirteen mutants against twelve rows, and is rewritten from the artefact rather than from memory)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/verify-corpus-baseline.txt, .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, tools/tests/test_verify_corpus.py, docs/release-notes-v5.0.1.md
> **Depends on:** BG0596 - `mutation.py run --story BG0592 --from-plan` reports 15 of its 18 declared rows until the join is keyed per row, so its mutation evidence cannot be read - let alone reviewed a fifth time - before BG0596 is Fixed
> **Created:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The corpus lane's own baseline defines its metric twice, and both times as red acceptance criteria `across stories already at Done`. The implementation counts every story the walker returns, at any status. Measured 2026-08-17 across 670 stories: 87 red in total, of which only 20 are on stories at Done. The other 67 sit on stories at Ready (62), Superseded (3) and Won't Implement (2) - work that was never claimed complete, so a red criterion there is unbuilt behaviour rather than a stale selector. The lane's remedy text tells the reader a rise means `a hand-edit or a test rename. Find it, fix it`, which is the wrong instruction for every one of those 67.

## Steps to Reproduce

Measured 2026-08-17 at aba6b577 by running the verifier over all 670 stories and partitioning the failures by the story's own Status field: Done 647 stories / 20 red; Ready 19 / 62; Superseded 2 / 3; Won't Implement 2 / 2 (87 in total, 20 of them on Done). An earlier partition of this same run read 21 on Done and 88 in total; 20/87 is the reading that reproduces, and the 21 is left recorded here rather than quietly dropped. `tools/verify-corpus-baseline.txt` records `red-criteria|52|executable acceptance criteria that FAIL when run, across stories already at Done` and its header repeats the Done wording. `gate.py`'s verify lane selects with `stories = list(verify_ac.walk_stories(rr / 'sdlc-studio' / 'stories'))` and applies no status filter before collecting `report.failures` into `red`. THE CORROBORATING EVIDENCE IS IN THE BASELINE'S OWN HEADER: it records the figure moving 106, then 53, then 58, then 50, then 52 and says the reading `could NOT be reproduced a day later on a tree whose stories are byte-identical - the DENOMINATOR differs`. A population that includes every un-started story moves whenever grooming happens, which is exactly what a metric about finished work should be immune to.

## Proposed Fix

Count what the metric says it counts: restrict the red tally to stories whose status CLAIMS the work is complete. Ready is unbuilt; Superseded and Won't Implement are abandoned; none of the three is a claim that anything was finished, so a red criterion on them says nothing about rot. Scope the RED collection rather than the verification, so the lane still executes every criterion and can still report the others separately - a story dropped from the count must not become a story nobody runs. The baseline must be LOWERED to the re-measured Done-only figure in the same commit, which the lane already demands in both directions. Pin it with a fixture holding one Done story with a red criterion and one Ready story with a red criterion, and assert the count is 1 - a test asserting only the total would pass on the defect.

## Acceptance Criteria

- [x] **AC1** Given a red criterion on a Done story and a red criterion on a Ready story, when the release verify lane counts, then it reports 1 red - the metric counts only what claims completion. A round-2 review found this criterion's own verifier could not discriminate it: it asserted `US0001` appeared SOMEWHERE in the detail, and under an inverted implementation it appears in the exclusion ledger while the count stays 1. The verifier now asserts the id inside the RED clause, so the inversion fails it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_red_criterion_on_a_ready_story_is_not_counted_as_red
  - **Verified:** yes (2026-08-17)
- [x] **AC2** Given a red criterion on a Superseded or Won't Implement story, when the lane counts, then it is not red - both are TERMINAL for a story, so a terminal-only test would count them, and neither asserts anything was finished.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_an_abandoned_story_claims_nothing_so_its_red_is_not_a_regression
  - **Verified:** yes (2026-08-17)
- [x] **AC3** Given a story carrying NO Status field at all, when the lane counts, then its red criterion IS counted - the exclusion must not be reachable by deleting a line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_story_with_no_status_is_counted_not_excused
  - **Verified:** yes (2026-08-17)
- [x] **AC4** Given a failing criterion excluded from the red count, when the lane reports, then it is named on its own line with the story's status - an exclusion nobody can see is one nobody can audit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_the_excluded_failures_are_still_reported
  - **Verified:** yes (2026-08-17)
- [x] **AC5** Given a red criterion on a Done story, when the lane runs, then it FAILS and blocks - the regression the lane exists to catch is untouched.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_red_criterion_on_a_done_story_still_fails_the_lane
  - **Verified:** yes (2026-08-17)
- [x] **AC6** Given a story that claims no completion, when the lane runs, then its criteria are still EXECUTED and reported in the scope line - narrowing the count must not narrow what is run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_narrowing_the_count_does_not_narrow_what_is_executed
  - **Verified:** yes (2026-08-17)

- [x] **AC7** Given a corpus whose only failing criteria are on stories claiming no completion, when the release lane runs, then it PASSES - the behaviour the whole change exists to deliver, which no criterion asserted until a review reverted it in one line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_corpus_whose_only_failures_claim_nothing_PASSES_the_lane
  - **Verified:** yes (2026-08-17)
- [x] **AC8** Given a Done status carrying release decoration, a misspelling, or an off-vocabulary value, when the lane counts, then the criterion IS counted - the exclusion must not be reachable by editing a status line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_decorated_or_misspelled_status_is_counted_not_excused
  - **Verified:** yes (2026-08-17)
- [x] **AC9** Given a criterion the trust boundary refused to RUN on a story claiming no completion, when the lane classifies it, then it stays BLOCKED rather than excluded - unproven is not the same fact as unbuilt.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_an_unrun_verifier_stays_BLOCKED_even_when_the_story_claims_nothing
  - **Verified:** yes (2026-08-17)
- [x] **AC10** Given more excluded criteria than the lane's elision cap, when it reports, then every one is named - a partial ledger of what was removed from the enforced number is the audit going missing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_every_excluded_row_is_named_not_just_the_first_ten
  - **Verified:** yes (2026-08-17)

- [x] **AC11** Given a project that DECLARES a story status in its `.config.yaml` and moves finished stories to it, when the lane classifies a red criterion on one, then it is COUNTED - a declared status is recognised by the extended vocabulary and can never be terminal in the module tables, so the first cut recognised it and then exempted it, losing every regression on a consuming project's completed work.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_project_declared_status_cannot_buy_an_exemption
  - **Verified:** yes (2026-08-18)

- [x] **AC12** Given a corpus whose only failures are excluded, so the lane renders PASS, when it reports, then it still carries the SCOPE disclosure and the green denominator - the first cut moved PASS onto a branch that had never needed the scope note, making BG0530 AC5 conditionally false exactly at the end state this change steers towards.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_pass_over_an_exclusion_ledger_still_discloses_its_scope
  - **Verified:** yes (2026-08-18)

- [x] **AC13** Given a PASS reached through the exclusion ledger, when the lane states its green figure, then that figure EXCLUDES every failing class - the first repair printed `executable`, which is everything that RAN, so one line read `3/3 green` beside `2 failing`. At the end state this change steers towards it would have claimed 1834 of 1906 green with 67 of those failing. Subtracting a subset is the same defect quieter, and a FAIL verdict states no green figure at all.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_the_green_figure_excludes_every_failing_class
  - **Verified:** yes (2026-08-18)

- [x] **AC14** Given a corpus with no acceptance criteria at all, when the lane refuses, then it still names the artefact classes it did not walk - the comment claimed the disclosure was on every verdict while two returns omitted it, which is the claim-versus-code gap round 2 blocked on, one branch across.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_the_no_criteria_refusal_discloses_its_scope_too
  - **Verified:** yes (2026-08-18)

- [x] **AC15** Given the release gate driven through the SHIPPED CLI as a subprocess, when the corpus carries a failing criterion on a story claiming no completion, then the command prints it as excluded and not as red. The only CLI-driven verifier on this unit, added because a review found the `Verification depth` field claiming several while every `Verify:` line resolved in-process.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_the_shipped_cli_prints_the_exclusion_verdict
  - **Verified:** yes (2026-08-19)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | delete the `claims_done` guard in gate.py, so every failure lands in the red list again | Given a red criterion on a Done story and a red criterion on a Ready story, when the release verify lane counts, then it reports 1 red - the metric counts only what claims completion. |
| AC2 | replace `is_delivered_terminal` with `is_terminal_status` in gate.py, leaving the bare terminal-set lookup (the original row named `_ABANDONED_STATUSES`, which this repair deleted, so it was unrunnable as written - found by a round-2 review re-running the plan) | Given a red criterion on a Superseded or Won't Implement story, when the lane counts, then it is not red - both are TERMINAL for a story, so a terminal-only test would count them, and neither asserts anything was finished. |
| AC3 | change `_claims_completion` in gate.py to return False for an absent status, so a story leaves the metric by dropping a line | Given a story carrying NO Status field at all, when the lane counts, then its red criterion IS counted - the exclusion must not be reachable by deleting a line. |
| AC4 | replace the `unbuilt.append` collection in gate.py with `pass`, dropping the excluded rows instead of reporting them | Given a failing criterion excluded from the red count, when the lane reports, then it is named on its own line with the story's status - an exclusion nobody can see is one nobody can audit. |
| AC5 | invert the guard in gate.py to `elif not claims_done`, counting everything except the finished work | Given a red criterion on a Done story, when the lane runs, then it FAILS and blocks - the regression the lane exists to catch is untouched. |
| AC6 | insert a `continue` in gate.py for stories claiming no completion, so their criteria are never executed | Given a story that claims no completion, when the lane runs, then its criteria are still EXECUTED and reported in the scope line - narrowing the count must not narrow what is run. |
| AC7 | change the count in gate.py to `len(red) + len(unbuilt)`, restoring the block on every excluded criterion | Given a corpus whose only failing criteria are on stories claiming no completion, when the release lane runs, then it PASSES - the behaviour the whole change exists to deliver, which no criterion asserted until a review reverted it in one line. |
| AC8 | replace the WHOLE predicate body in gate.py with `return status in {"Done"}` - dropping the fail-closed branch with the canonical lookup. Sharpened after a round-3 review ran the looser wording, kept fail-closed, and got a SURVIVOR: a set match that still fails closed is equivalent here, so the row named a mutant a reviewer could read two ways and get two answers | Given a Done status carrying release decoration, a misspelling, or an off-vocabulary value, when the lane counts, then the criterion IS counted - the exclusion must not be reachable by editing a status line. |
| AC9 | add `and claims_done` to the blocked branch in gate.py, so an unrun verifier is reclassified | Given a criterion the trust boundary refused to RUN on a story claiming no completion, when the lane classifies it, then it stays BLOCKED rather than excluded - unproven is not the same fact as unbuilt. |
| AC10 | pass the exclusion ledger in gate.py through `_elide`, truncating it to the first ten | Given more excluded criteria than the lane's elision cap, when it reports, then every one is named - a partial ledger of what was removed from the enforced number is the audit going missing. |
| AC11 | restore the root PARAMETER and classify against `status_vocab("story", Path(root))`, resolving the run's actual root. Passing cwd instead is EQUIVALENT and survives, because a fixture's `.config.yaml` lives under `--root` and never under cwd - found by a round-3 review, and the reason the row names the parameter rather than the call | Given a project that DECLARES a story status in its `.config.yaml` and moves finished stories to it, when the lane classifies a red criterion on one, then it is COUNTED. |
| AC12 | drop `scope_note` from the `if parts:` return in gate.py, so a PASS reached through the exclusion ledger discloses nothing | Given a corpus whose only failures are excluded, so the lane renders PASS, when it reports, then it still carries the SCOPE disclosure and the green denominator. |
| AC13 | report `executable` as the green count on the exclusion-only PASS, so everything that RAN is claimed as green | Given a PASS reached through the exclusion ledger, when the lane states its green figure, then that figure EXCLUDES every failing class. |
| AC13 | subtract only `red`, leaving the excluded failures inside the green count | Subtracting a SUBSET is the same defect quieter. |
| AC13 | emit the green clause unconditionally, so a FAIL verdict carries a green claim | A FAIL states no green figure at all. |
| AC13 | count MANUAL criteria as green (`passing = acs - len(unbuilt)`) - every fixture had `manual=0`, so this SURVIVED until a review demonstrated it and the fixture gained a manual criterion | The green figure counts only what executed AND passed. |
| AC15 | revert the `claims_done` guard and ask whether the SHIPPED CLI still prints the exclusion verdict - the wiring mutant, because a library test cannot see whether the lane is reached by the command an operator runs | Given the release gate driven as a subprocess, when the corpus carries a failure on a story claiming no completion, then the CLI prints it as excluded rather than red. |
| AC14 | drop `scope_note` from the no-acceptance-criteria return in gate.py | Given a corpus with no acceptance criteria at all, when the lane refuses, then it still names the artefact classes it did not walk. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | Round 2 REJECT repaired: AC11 (a project-declared status bought a silent exemption - recognised by the extended vocab, unclassifiable by the module tables) and AC12 (a PASS reached through the exclusion ledger disclosed no scope). AC1's verifier could not discriminate its own claim. Mutation record corrected 9 -> 13; AC2's declared mutant named deleted code. Stale 68/21 and a stale ordinal cleared from durable prose; the shipped release-gate workflow still promised the old contract |
| 2026-08-18 | sdlc-studio | Round 3 REJECT repaired. AC13: the green figure printed `executable`, everything that RAN, so one line read `3/3 green` beside `2 failing` - the false-green-over-a-fraction this unit indicts, reintroduced by the sentence written to repair it, and unpinned because the test asserted a substring. AC14: two returns omitted the scope note the new comment claimed was on every verdict. A `Verified:` stamp had been orphaned onto AC12 dated before AC12 existed, taking AC10's real one with it. `Affects` widened to the nine files this unit actually changed - as declared, the seat brief scoped its own reviewer away from four of them |
| 2026-08-19 | sdlc-studio | Round 4 REJECT repaired. AC13 had an equivalent-fixture hole: every fixture carried `manual=0`, so `passing = acs - len(unbuilt)` counted manual criteria as green and SURVIVED - the same green-over-a-fraction AC13 forbids, at the scale it names. AC15 added: this field claimed CLI coverage that did not exist, for the fifth successive time, so the coverage was added rather than the sentence softened |
