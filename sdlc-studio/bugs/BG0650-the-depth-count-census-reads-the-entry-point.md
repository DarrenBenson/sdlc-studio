# BG0650: The depth-count census reads the entry-point denominator, so an artefact with a manual criterion fails it

> **Status:** Fixed
> **Verification depth:** functional [[derived: criteria 1; plan rows 3; executed 3; killed 3; survived 0; not-run 0; entry point 0 of 1 criteria through the shipped CLI, 1 in-process | fp c2d3b0890f89 ]]
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_known_issues.py
> **Evidence:** BG0641 engineering seat, delivery r2, 2026-09-04; reproduced on this tree with BG0641's derived field. Depth derivation is CR0548's area.
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`tools/tests/test_known_issues.py::DepthFieldCountsTests::test_no_depth_field_states_a_criterion_count_the_artefact_contradicts` takes the FIRST `<n> criteria` match in a derived `Verification depth` field. The deriver writes the total as `criteria 9` (count after the word, never matched) and the entry-point figure as `6 of 8 criteria through the shipped CLI`, which excludes manual criteria; the census reads the 8, compares it with all 9 ACs and reports a contradiction that does not exist. BG0641, the first artefact with a manual criterion and a derived field, refuses every commit through the tools suite.

## Steps to Reproduce

1. Give a bug artefact nine ACs, one with `Verify: manual`, and run `verify_ac.py depth --unit <id> --write`.
2. `python3 -B -m pytest -p no:cacheprovider tools/tests/test_known_issues.py -k depth_field`.
3. Observe `<id>: depth says 8, artefact has 9`.

## Proposed Fix

Read the deriver's own total (`criteria (\d+)`) first and fall back to the hand-written `<n> criteria` form; the entry-point denominator is a count of executable criteria and is not the figure the census compares.

## Acceptance Criteria

- [x] **AC1** Given a derived depth field whose total says nine criteria and whose entry-point figure says eight, on an artefact with nine ACs one of which is manual, when the census runs, then it reads the total and reports no contradiction; and a field whose total disagrees with the artefact is still reported.
  - **Verify:** pytest tools/tests/test_known_issues.py::DepthFieldCountsTests::test_the_census_reads_the_derived_total_not_the_entry_point_denominator
  - **Verified:** yes (2026-09-04)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `tools/tests/test_known_issues.py`, read the first `<n> criteria` match again, as before BG0650, so the entry-point denominator is taken for the total | Given a derived depth field whose total says nine criteria and whose entry-point figure says eight, on an artefact with nine ACs one of which is manual, when the census runs, then it reads the total and reports no contradiction; and a field whose total disagrees with the artefact is still reported. |
| AC1 | in `tools/tests/test_known_issues.py`, return the entry-point denominator (`of (\d+) criteria`) as the stated total | Given a derived depth field whose total says nine criteria and whose entry-point figure says eight, on an artefact with nine ACs one of which is manual, when the census runs, then it reads the total and reports no contradiction; and a field whose total disagrees with the artefact is still reported. |
| AC1 | in `tools/tests/test_known_issues.py`, return None for any derived field, silencing the census for every derived artefact | Given a derived depth field whose total says nine criteria and whose entry-point figure says eight, on an artefact with nine ACs one of which is manual, when the census runs, then it reads the total and reports no contradiction; and a field whose total disagrees with the artefact is still reported. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
