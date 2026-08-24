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

- [ ] **AC1** Given three changes of known size against the SAME large production file - one point, three points, eight points across four files - when each is scored on the DECLARED basis, then they land in three DIFFERENT bands in that order. This is the claim CR0549 makes and the one whole-file complexity cannot satisfy
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_three_known_sizes_against_one_file_band_differently
- [ ] **AC2** Given those same three changes, when their scores are compared, then each is separated from the next by at least a stated minimum - asserted as that number, not as an interquartile spread, because a quartile over three points is not a statistic
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_the_three_scores_are_separated_by_the_stated_minimum
- [ ] **AC3** Given this repository's whole bug corpus scored on the DECLARED basis, when the distribution is measured after the change, then `light` is at least 30% where it is 13% today - measured IN the test against the corpus as it stands, never against percentages copied from the CR, because the corpus grows and a hard-coded percentile is falsified by filing an unrelated bug
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_the_declared_basis_moves_light_above_thirty_percent
- [ ] **AC4** Given both measurements, when the delivery records them in CR0549, then the recorded figures are produced by RUNNING the measurement command and pasting its output, and the criterion is discharged by that command exiting zero - not by a test asserting that a document matches a fresh run of the code that wrote it, which passes by construction
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_the_measurement_command_runs_and_reports_both_bases

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |

| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
