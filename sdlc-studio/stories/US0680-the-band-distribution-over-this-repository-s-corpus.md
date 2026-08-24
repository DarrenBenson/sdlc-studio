# US0680: The band distribution over this repository's corpus is RE-MEASURED after the change and recorded, so the claim that the gate discriminates rests on a number

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py, sdlc-studio/change-requests/CR0549-route-estimate-scores-whole-declared-files-so-the.md
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The band distribution over this repository's corpus is RE-MEASURED after the change and recorded, so the claim that the gate discriminates rests on a number
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a SYNTHETIC corpus of changes whose expected bands are known in advance - a one-line edit, a small localised edit and a whole-module rewrite, each against the SAME large production file - when each is scored on the DIFF basis, then they land in different bands in that order. The corpus is synthetic by necessity: 603 closed bugs carry no per-unit diff, so a re-measurement over them can only use the declared basis and would re-measure the estimator this change replaces
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_three_known_changes_to_one_file_band_differently
- [ ] **AC2** Given that synthetic corpus, when the interquartile spread of its diff-basis scores is computed, then it is WIDER than the six-point spread the declared basis produces over the same three changes - stated as a number the test asserts, because "the gate now discriminates" is exactly the kind of claim this project has shipped false before
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_the_diff_basis_spread_is_wider_than_the_declared_basis
- [ ] **AC3** Given this repository's whole bug corpus scored on the DECLARED basis, when the distribution is re-measured after the change, then it is UNCHANGED from the pre-change figures - 87% full, 48% with `code` and `risk` both saturated, p25-median-p75 of 48-50-54 - because the declared basis is what those figures always measured. The paired control: a change that moved this number would mean the declared path had been altered by accident
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_the_declared_basis_distribution_is_unchanged
- [ ] **AC4** Given both measurements, when they are recorded, then BOTH are written into CR0549 beside the pre-change figures, with the basis named against each - a single number with no basis stated is the conflation this whole change exists to remove
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_both_recorded_distributions_match_a_fresh_measurement

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | HELD - not in the RUN batch. CR0549's correction of 2026-08-21 applies: AC1 asserts a markdown document matches a fresh run of the code that wrote it, which passes by construction, and AC2 asserts a widening that AC1 of US0678 makes impossible for a corpus of closed units. What a corpus re-measurement can honestly mean is unsettled - see the CR. Re-groom before planning. |
