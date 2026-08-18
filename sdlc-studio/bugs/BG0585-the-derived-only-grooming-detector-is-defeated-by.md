# BG0585: the derived-only grooming detector is defeated by the AC-number prefix it ships with

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`is_derived_criterion` strips the leading bullet, the checkbox and the `**` emphasis, then matches the remainder against patterns anchored at `^The behaviour described is corrected:` and its four siblings. It does NOT strip the `ACn` number, so a criterion written as `- [ ] **AC1** The behaviour described is corrected: ...` leaves the body `AC1 The behaviour described is corrected: ...` and matches nothing. `conformance.unit_is_ungroomed` therefore reports `(False, '')` - GROOMED - for the numbered form, and `(True, 'derived-only')` for the otherwise identical unnumbered one. The `derived-only` shape is the one conformance.py's own docstring calls 'the shape that reads like content and is not'. Stronger than first filed: `criteria_block` emits ONLY the numbered form, so the detector matches ZERO output of its own writer. `is_derived_criterion` shipped 2026-08-04 and the `**ACn**` marker was added 2026-08-06, so the limb has been wholly inert for twelve days and for every filing since. The corpus shows only four flips because most recent filings carried authored criteria - the low number measures luck, not exposure.

## Steps to Reproduce

Measured 2026-08-16 at 7697ee36 by calling the shipped predicate on two texts differing only in the `**ACn**` prefix. `conformance.unit_is_ungroomed('bug', '## Acceptance Criteria\n\n- [ ] **AC1** The behaviour described is corrected: the thing is fixed.\n- [ ] **AC2** The proposed fix lands, pinned by a test: the fix lands.\n')` returns `(False, '')`. The same text with the AC-number prefixes removed returns `(True, 'derived-only')`. Both forms occur in this repository: the numbered form is what BG0582 itself carried when filed, and `sprint plan`'s own refusal message quotes it verbatim as the scaffold it rejects - `- [ ] **AC1** The behaviour described is corrected: <restates the summary>`.

## Proposed Fix

Strip a leading `ACn` token in `is_derived_criterion` before matching, in the same pass that already strips the bullet, the checkbox and the emphasis - the module's `AC_HEADING_RE` equivalent already knows the shape, so read it from there rather than adding a second spelling. Pin BOTH forms in one test: the existing coverage passes on the unnumbered form alone, which is why this survived. Check the same prefix assumption in the other consumers of `criteria_are_all_derived` before assuming this is the only one.

## Acceptance Criteria

- [ ] **AC1** Given a criterion the shipped WRITER emits - `criteria_block` produces only the `- [ ] **ACn** ...` form - when `is_derived_criterion` reads it, then it returns True. Measured through the writer, not a hand-typed string.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_detector_matches_its_own_writers_output
- [ ] **AC2** Given the same criterion with no `ACn` prefix, when it reads it, then it still returns True - the existing form must not regress.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_unnumbered_form_still_matches
- [ ] **AC3** Given an authored criterion carrying an `ACn` prefix and real content, when it reads it, then it returns False - the positive control, so stripping the number does not make every numbered criterion derived.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_an_authored_numbered_criterion_is_not_derived
- [ ] **AC4** Given the `### ACn:` heading form, which `criteria_are_all_derived` deliberately collects, when the detector reads it, then it returns True - `###` is never stripped by the proposed fix, and an enumerated list silently exempts what it forgot.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_heading_form_matches_too
- [ ] **AC5** Given a batch naming a unit whose criteria are the numbered derived scaffold, when `sprint.py plan` runs, then it REFUSES naming `derived-only` - driven through the shipped CLI, because a library test cannot see whether the predicate is wired, which is the fault that let `brief_fingerprint` pass for a whole sprint while the CLI printed nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_sprint_plan_refuses_the_numbered_scaffold
- [ ] **AC6** Given the corpus, when the census is recomputed with the fix, then exactly 4 bugs flip to `derived-only` (BG0537, BG0547, BG0578, BG0581) and 0 stories - two seats measured this independently, and any other number means the fix over- or under-reaches.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_corpus_census_moves_by_exactly_four

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
