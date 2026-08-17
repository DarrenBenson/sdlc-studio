# BG0592: the corpus red-criteria metric counts unbuilt stories, which is why its number has never been stable

> **Status:** Open
> **Severity:** High
> **Verification depth:** functional (all ten criteria drive the real release lane over temp corpora at seven story statuses. Mutation: 9 mutants, each anchor asserted unique, `__pycache__` purged and `python3 -B`, all 9 KILLED, restore byte-exact - THREE of them from a review that REJECTED the first cut, including one that reverted the entire repair in a single line while all fourteen tests stayed green. Re-measured end to end through `verify-corpus.sh`: 20 red where the lane reported 88, with the 67 excluded rows printed in full with their statuses. THREE false readings were taken and discarded before the baseline moved - 26, inflated by the author's own uncommitted style violation breaking a lane six criteria invoke; a per-AC 21 whose extra row was a load timeout; and an 88/68/21 arithmetic carried into durable prose after the measurement had already corrected it to 87/67/20)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/verify-corpus-baseline.txt
> **Created:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The corpus lane's own baseline defines its metric twice, and both times as red acceptance criteria `across stories already at Done`. The implementation counts every story the walker returns, at any status. Measured 2026-08-17 across 670 stories: 87 red in total, of which only 20 are on stories at Done. The other 67 sit on stories at Ready (62), Superseded (3) and Won't Implement (2) - work that was never claimed complete, so a red criterion there is unbuilt behaviour rather than a stale selector. The lane's remedy text tells the reader a rise means `a hand-edit or a test rename. Find it, fix it`, which is the wrong instruction for every one of those 67.

## Steps to Reproduce

Measured 2026-08-17 at aba6b577 by running the verifier over all 670 stories and partitioning the failures by the story's own Status field: Done 647 stories / 21 red; Ready 19 / 62; Superseded 2 / 3; Won't Implement 2 / 2. `tools/verify-corpus-baseline.txt` records `red-criteria|52|executable acceptance criteria that FAIL when run, across stories already at Done` and its header repeats the Done wording. `gate.py`'s verify lane selects with `stories = list(verify_ac.walk_stories(rr / 'sdlc-studio' / 'stories'))` and applies no status filter before collecting `report.failures` into `red`. THE CORROBORATING EVIDENCE IS IN THE BASELINE'S OWN HEADER: it records the figure moving 106, then 53, then 58, then 50, then 52 and says the reading `could NOT be reproduced a day later on a tree whose stories are byte-identical - the DENOMINATOR differs`. A population that includes every un-started story moves whenever grooming happens, which is exactly what a metric about finished work should be immune to.

## Proposed Fix

Count what the metric says it counts: restrict the red tally to stories whose status CLAIMS the work is complete. Ready is unbuilt; Superseded and Won't Implement are abandoned; none of the three is a claim that anything was finished, so a red criterion on them says nothing about rot. Scope the RED collection rather than the verification, so the lane still executes every criterion and can still report the others separately - a story dropped from the count must not become a story nobody runs. The baseline must be LOWERED to the re-measured Done-only figure in the same commit, which the lane already demands in both directions. Pin it with a fixture holding one Done story with a red criterion and one Ready story with a red criterion, and assert the count is 1 - a test asserting only the total would pass on the defect.

## Acceptance Criteria

- [ ] **AC1** Given a red criterion on a Done story and a red criterion on a Ready story, when the release verify lane counts, then it reports 1 red - the metric counts only what claims completion.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_red_criterion_on_a_ready_story_is_not_counted_as_red
  - **Verified:** yes (2026-08-17)
- [ ] **AC2** Given a red criterion on a Superseded or Won't Implement story, when the lane counts, then it is not red - both are TERMINAL for a story, so a terminal-only test would count them, and neither asserts anything was finished.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_an_abandoned_story_claims_nothing_so_its_red_is_not_a_regression
  - **Verified:** yes (2026-08-17)
- [ ] **AC3** Given a story carrying NO Status field at all, when the lane counts, then its red criterion IS counted - the exclusion must not be reachable by deleting a line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_story_with_no_status_is_counted_not_excused
  - **Verified:** yes (2026-08-17)
- [ ] **AC4** Given a failing criterion excluded from the red count, when the lane reports, then it is named on its own line with the story's status - an exclusion nobody can see is one nobody can audit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_the_excluded_failures_are_still_reported
  - **Verified:** yes (2026-08-17)
- [ ] **AC5** Given a red criterion on a Done story, when the lane runs, then it FAILS and blocks - the regression the lane exists to catch is untouched.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_red_criterion_on_a_done_story_still_fails_the_lane
  - **Verified:** yes (2026-08-17)
- [ ] **AC6** Given a story that claims no completion, when the lane runs, then its criteria are still EXECUTED and reported in the scope line - narrowing the count must not narrow what is run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_narrowing_the_count_does_not_narrow_what_is_executed
  - **Verified:** yes (2026-08-17)

- [ ] **AC7** Given a corpus whose only failing criteria are on stories claiming no completion, when the release lane runs, then it PASSES - the behaviour the whole change exists to deliver, which no criterion asserted until a review reverted it in one line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_corpus_whose_only_failures_claim_nothing_PASSES_the_lane
  - **Verified:** yes (2026-08-17)
- [ ] **AC8** Given a Done status carrying release decoration, a misspelling, or an off-vocabulary value, when the lane counts, then the criterion IS counted - the exclusion must not be reachable by editing a status line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_a_decorated_or_misspelled_status_is_counted_not_excused
  - **Verified:** yes (2026-08-17)
- [ ] **AC9** Given a criterion the trust boundary refused to RUN on a story claiming no completion, when the lane classifies it, then it stays BLOCKED rather than excluded - unproven is not the same fact as unbuilt.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_an_unrun_verifier_stays_BLOCKED_even_when_the_story_claims_nothing
  - **Verified:** yes (2026-08-17)
- [ ] **AC10** Given more excluded criteria than the lane's elision cap, when it reports, then every one is named - a partial ledger of what was removed from the enforced number is the audit going missing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RedCountsOnlyWhatClaimsCompletionTests::test_every_excluded_row_is_named_not_just_the_first_ten
  - **Verified:** yes (2026-08-17)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | delete the `claims_done` guard in gate.py, so every failure lands in the red list again | Given a red criterion on a Done story and a red criterion on a Ready story, when the release verify lane counts, then it reports 1 red - the metric counts only what claims completion. |
| AC2 | delete the `_ABANDONED_STATUSES` membership test from gate.py, leaving the bare terminal-set lookup | Given a red criterion on a Superseded or Won't Implement story, when the lane counts, then it is not red - both are TERMINAL for a story, so a terminal-only test would count them, and neither asserts anything was finished. |
| AC3 | change `_claims_completion` in gate.py to return False for an absent status, so a story leaves the metric by dropping a line | Given a story carrying NO Status field at all, when the lane counts, then its red criterion IS counted - the exclusion must not be reachable by deleting a line. |
| AC4 | replace the `unbuilt.append` collection in gate.py with `pass`, dropping the excluded rows instead of reporting them | Given a failing criterion excluded from the red count, when the lane reports, then it is named on its own line with the story's status - an exclusion nobody can see is one nobody can audit. |
| AC5 | invert the guard in gate.py to `elif not claims_done`, counting everything except the finished work | Given a red criterion on a Done story, when the lane runs, then it FAILS and blocks - the regression the lane exists to catch is untouched. |
| AC6 | insert a `continue` in gate.py for stories claiming no completion, so their criteria are never executed | Given a story that claims no completion, when the lane runs, then its criteria are still EXECUTED and reported in the scope line - narrowing the count must not narrow what is run. |
| AC7 | change the count in gate.py to `len(red) + len(unbuilt)`, restoring the block on every excluded criterion | Given a corpus whose only failing criteria are on stories claiming no completion, when the release lane runs, then it PASSES - the behaviour the whole change exists to deliver, which no criterion asserted until a review reverted it in one line. |
| AC8 | replace the canonical lookup in gate.py with a literal set match on the raw status text | Given a Done status carrying release decoration, a misspelling, or an off-vocabulary value, when the lane counts, then the criterion IS counted - the exclusion must not be reachable by editing a status line. |
| AC9 | add `and claims_done` to the blocked branch in gate.py, so an unrun verifier is reclassified | Given a criterion the trust boundary refused to RUN on a story claiming no completion, when the lane classifies it, then it stays BLOCKED rather than excluded - unproven is not the same fact as unbuilt. |
| AC10 | pass the exclusion ledger in gate.py through `_elide`, truncating it to the first ten | Given more excluded criteria than the lane's elision cap, when it reports, then every one is named - a partial ledger of what was removed from the enforced number is the audit going missing. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
