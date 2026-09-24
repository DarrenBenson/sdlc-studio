# BG0732: the derived-only corpus ceiling is an absolute count, so a run that files findings breaches it without the detector over-reaching

> **Status:** Superseded
> **Closed with findings in:** Superseded by BG0742 (RUN-01M39MC0), which moved the derived-only census onto verbatim fixture copies and removed the live-corpus ceiling this finding was about.
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`DerivedDetectorSeesItsOwnWriterTests::test_the_corpus_census_stays_within_its_measured_bounds` asserts that fewer than 60 bugs in the corpus read `derived-only`. Its purpose is to catch `is_derived_criterion` over-reaching and eating authored prose, and its docstring says so: a review once mutated the predicate to return True unconditionally and every shape assertion still passed while the census went from 17 bugs to 364. The NUMBER is the claim, and it is the right claim. But the ceiling is ABSOLUTE while the quantity it bounds grows with the corpus. A freshly filed bug carries the filer's two derived criteria by construction and reads derived-only until it is groomed, so the census rises by one for every finding anybody files. RUN-01M306PY filed twelve in a day - its whole purpose was re-triaging an aggregate into artefacts that can be planned - and took the census from 51 to 63. The detector did not change. The docstring anticipates exactly this and says `filing or grooming a bug must not turn this red`, which is the behaviour the current form cannot deliver.

## Steps to Reproduce

1. Note the census: 63 bugs read derived-only at HEAD, against a ceiling of 60. 2. `git log` shows no change to `is_derived_criterion` or `unit_is_ungroomed` in the runs that moved it. 3. File any finding through `file_finding.py` without grooming it. 4. The census rises by one, and the guard is one bug closer to red for a reason unrelated to detector reach.

## Proposed Fix

Bound the RATIO rather than the count, or bound the count of bugs that have been open long enough to have been groomed. The signal the test wants is `the detector is eating authored prose`, and the mutation it defends against took the census to 364 of roughly 370 - a ratio near 1.0 - so a ratio ceiling around 0.15 keeps all of the original discrimination while surviving a corpus that grows and a run whose output is filed findings. Keep the stories-at-zero assertion exactly as it is: the story corpus is wholly authored, so zero is an exact claim there and the strongest half of the test. Record the measured ratio in the docstring the way the count is recorded now.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `DerivedDetectorSeesItsOwnWriterTests::test_the_corpus_census_stays_within_its_measured_bounds` asserts that fewer than 60 bugs in the corpus read...
- [ ] **AC2** The proposed fix lands, pinned by a test: Bound the RATIO rather than the count, or bound the count of bugs that have been open long enough to have been groomed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Superseded by BG0742: the census no longer reads the live corpus |
