# BG1734: BG1548 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md, sdlc-studio/rfcs/RFC0064-production-learning-and-risk-proportionate-review.md, tools/lint_corpus.py, tools/tests/test_lint_corpus.py, changelog.d/BG1548.md
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T02:52:39Z

## Summary

BG1548 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's heading test pins the end anchor against the plural only: `test_only_a_heading_reading_decision_alone_opens_the_decision_section` (`tools/tests/test_lint_corpus.py`) says only a heading reading Decision alone opens the section. Yet with the pattern's `[ \t]*$` replaced by `\b` (`tools/lint_corpus.py:65`), every test in `AcceptedRfcDecisionTests` and `CorpusLaneRunsOnThisRepo` still passes. Run alone on an Accepted RFC headed `## Decision (accepted 2026-11-14)` above `**Outcome:** pending`, the shipped pattern reports nothing and the mutant reports the RFC. No test decides whether a Decision heading with a suffix opens the section, so a pending Outcome under one reads clean with nothing pinning that; [pre-existing] `tools/tests/test_lint_corpus.py:52` calls `find_linter` at import (line 51 at the base), so without markdownlint the module fails to collect. That is why the brief's replay reads error for all five author mutants. No open bug covers it (BG1147, the nearest, is Fixed); RULINGS: Round-one findings, each judged by execution at a35d93e25 with MARKDOWNLINT\_BIN set. "The changelog overstates which workstream rows lacked a unit" is CLOSED: `changelog.d/BG1548.md` now names WS2, WS5's budget view, WS6's scorecard and WS7 as the work no unit carried, and WS1, WS3 and WS5's pricing as naming CR0689, CR0702 and CR0690, which were already decomposed. That matches the base Decomposed-into line and the cells at HEAD. "RFC0063's Revision History row" is CLOSED: the row at RFC0063 line 204 now records the rewrite of the Becomes cells for WS1, WS2, WS3, WS5, WS6 and WS7, and the row is pinned (a mutant dropping WS7 from it is KILLED by `test_rfc0063_deferred_workstreams_name_a_request_or_ruling`). "The change to `lint_corpus()` has no test" is CLOSED: the markdownlint-only mutant is KILLED by `test_an_accepted_rfc_with_a_pending_outcome_is_reported`. "The end anchor of the Decision heading pattern has no test" is OVER-CLAIMED: the mutant that drops `[ \t]*$` is now KILLED and the `## Decisions (...)` case the finding named is decided, but the commit's "pins the Decision heading pattern's end anchor" holds only against the plural, because the `\b` replacement survives (the ISSUES finding). analyse and the baseline dropping the rule are both KILLED again. The test docstring's RFC0020 is the corpus file holding `## Decisions (resolved by the consultation)` (TRUE). "Deferred past 6.4 by D0474" stays UNVERIFIABLE, as ruled in round one. `test_lint_corpus.py`, `test_lint_corpus_attribution.py`, `test_lean_prd_refresh.py`, `test_lean_config_keys_read.py` and `test_lean_breaking_inventory.py`: 55 passed. verify\_ac BG1548 --dry-run passes 3/3. Four of the author's five mutants are reproduced as killed by my equivalents. The fifth is a fixture mutant and was not re-run.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1548 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1548 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's heading test pins the end anchor against the plural only: `test_only_a_heading_reading_decision_alone_opens_the_decision_section` (`tools/tests/test_lint_corpus.py`) says only a heading reading Decision alone opens the section. Yet with the pattern's `[ \t]*$` replaced by `\b` (`tools/lint_corpus.py:65`), every test in `AcceptedRfcDecisionTests` and `CorpusLaneRunsOnThisRepo` still passes. Run alone on an Accepted RFC headed `## Decision (accepted 2026-11-14)` above `**Outcome:** pending`, the shipped pattern reports nothing and the mutant reports the RFC. No test decides whether a Decision heading with a suffix opens the section, so a pending Outcome under one reads clean with nothing pinning that
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] `tools/tests/test_lint_corpus.py:52` calls `find_linter` at import (line 51 at the base), so without markdownlint the module fails to collect. That is why the brief's replay reads error for all five author mutants. No open bug covers it (BG1147, the nearest, is Fixed)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1548 AC1 still passes: Given a fixture corpus holding an Accepted RFC whose Decision Outcome still reads pending, when `tools/lint_corpus.py` runs, then it reports a finding naming that RFC; a Proposed RFC with a pending Outcome and an Accepted RFC with a filled Decision beside it are not reported. Fails on: an Accepted RFC with an unfilled Decision reading as clean, or a finding against an RFC not yet decided.
  - **Verify:** pytest tools/tests/test_lint_corpus.py::AcceptedRfcDecisionTests::test_an_accepted_rfc_with_a_pending_outcome_is_reported
  - **Verified:** yes (2026-11-24)
- [ ] **AC4** BG1548 AC2 still passes: Given this repository's RFCs after the fix, when the new rule reads them, then it reports nothing: the Decision sections of RFC0063 and RFC0064 state the outcome, the date, the rationale, the decisions that resolved each open question and the spawned CRs. Fails on: either RFC still reading pending under Status Accepted.
  - **Verify:** pytest tools/tests/test_lint_corpus.py::CorpusLaneRunsOnThisRepo::test_no_accepted_rfc_here_has_a_pending_decision
  - **Verified:** yes (2026-11-24)
- [ ] **AC5** BG1548 AC3 still passes: Given RFC0063's workstream table after the fix, when rows WS2, WS5 (the monthly budget view), WS6 (the model scorecard) and WS7 are read, then each names a CR that is also in the Decomposed-into line, or the decision that defers it, and each RFC carries a Revision History row for the correction. Fails on: a workstream row promising a new CR that no unit or recorded deferral carries.
  - **Verify:** pytest tools/tests/test_lint_corpus.py::CorpusLaneRunsOnThisRepo::test_rfc0063_deferred_workstreams_name_a_request_or_ruling
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | sdlc-studio | Filed |
