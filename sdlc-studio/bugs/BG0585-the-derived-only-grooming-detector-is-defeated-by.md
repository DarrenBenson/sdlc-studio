# BG0585: the derived-only grooming detector is defeated by the AC-number prefix it ships with

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Verification depth:** functional (all six criteria drive the real detector, and AC5 drives `sprint.py plan` through the CLI by subprocess WITH A POSITIVE CONTROL in the same fixture - the first cut named `plan` in the criterion and ran `breakdown` in the test, which is read-only and exits 0, so no refusal was ever asserted and the wiring guarantee the criterion exists for was the one thing it did not check. AC6 pins the census COUNT and the empty story set, not four named ids: a review made the detector return True unconditionally - 17 bugs/0 stories to 364/669 - and the id assertions still passed. AC6's test also resolved the repo root to `.claude/`, so its glob matched nothing and every assertion was skipped; it measured nothing at all. Mutation: 10 mutants across two rounds, each anchor asserted unique, `__pycache__` purged and `python3 -B`, all 10 KILLED, restore byte-exact. THE FIRST ROUND'S RECORD WAS FALSE: a review re-ran it and found AC3's mutant SURVIVED all 6603 tests and AC6's was behaviourally inert)
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

- [x] **AC1** Given a criterion the shipped WRITER emits - `criteria_block` produces only the `- [ ] **ACn** ...` form - when `is_derived_criterion` reads it, then it returns True. Measured through the writer, not a hand-typed string.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_detector_matches_its_own_writers_output
  - **Verified:** yes (2026-08-18)
- [x] **AC2** Given the same criterion with no `ACn` prefix, when it reads it, then it still returns True - the existing form must not regress.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_unnumbered_form_still_matches
  - **Verified:** yes (2026-08-18)
- [x] **AC3** Given an authored criterion carrying an `ACn` prefix and real content, when it reads it, then it returns False - the positive control, so stripping the number does not make every numbered criterion derived.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_an_authored_numbered_criterion_is_not_derived
  - **Verified:** yes (2026-08-18)
- [x] **AC4** Given the `### ACn:` heading form, which `criteria_are_all_derived` deliberately collects, when the detector reads it, then it returns True - `###` is never stripped by the proposed fix, and an enumerated list silently exempts what it forgot.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_heading_form_matches_too
  - **Verified:** yes (2026-08-18)
- [x] **AC5** Given a batch naming a unit whose criteria are the numbered derived scaffold, when `sprint.py plan` runs, then it REFUSES naming `derived-only` - driven through the shipped CLI, because a library test cannot see whether the predicate is wired, which is the fault that let `brief_fingerprint` pass for a whole sprint while the CLI printed nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_sprint_plan_refuses_the_numbered_scaffold
  - **Verified:** yes (2026-08-18)
- [x] **AC6** Given the corpus, when the census is recomputed with the fix, then the four bugs two seats measured independently (BG0537, BG0547, BG0578, BG0581) read `derived-only`, the total stays under a ceiling, and NO story does. The count is bounded rather than exact because filing a bug with tool-derived criteria legitimately adds one and grooming it takes it away again: BG0595, filed in this same line of work, made the census read 18 until it was groomed, and 17 after. A review measured the 18 and was right at the moment it looked. That is exactly why this criterion asserts a CEILING and the four named ids rather than a single number - the population moves whenever anybody files or grooms, which is the same property that made the corpus red-criteria figure move five times - two seats measured this independently, and any other number means the fix over- or under-reaches.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DerivedDetectorSeesItsOwnWriterTests::test_the_corpus_census_moves_by_exactly_four
  - **Verified:** yes (2026-08-18)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in file_finding.py, delete the `_AC_NUMBER_RE.sub` line from `is_derived_criterion`, restoring the state in which the detector could not read its own writer's output | Given a criterion the shipped WRITER emits - `criteria_block` produces only the `- [ ] **ACn** ...` form - when `is_derived_criterion` reads it, then it returns True. Measured through the writer, not a hand-typed string. |
| AC2 | in file_finding.py, anchor `_AC_NUMBER_RE` with `re.fullmatch` semantics so a line WITHOUT an `ACn` label no longer reaches the pattern match | Given the same criterion with no `ACn` prefix, when it reads it, then it still returns True - the existing form must not regress. |
| AC3 | in file_finding.py, widen `_AC_NUMBER_RE` to `^AC\\w*\\s*:?\\s*`, so `ACCEPTED:` is eaten and authored prose starts reading as derived | Given an authored criterion carrying an `ACn` prefix and real content, when it reads it, then it returns False - the positive control, so stripping the number does not make every numbered criterion derived. |
| AC4 | in file_finding.py, drop the `.lstrip("#")` from the body normalisation, so the `### ACn:` heading form stops matching | Given the `### ACn:` heading form, which `criteria_are_all_derived` deliberately collects, when the detector reads it, then it returns True - `###` is never stripped by the proposed fix, and an enumerated list silently exempts what it forgot. |
| AC5 | in file_finding.py, revert `is_derived_criterion` to its pre-fix body and ask whether `sprint.py plan` still REFUSES with a non-zero exit - the WIRING mutant. The test must drive `plan`, not `breakdown`: the latter is read-only, exits 0, and its assertions held identically for a fixture with no criteria at all | Given a batch naming a unit whose criteria are the numbered derived scaffold, when `sprint.py plan` runs, then it REFUSES naming `derived-only` - driven through the shipped CLI, because a library test cannot see whether the predicate is wired, which is the fault that let `brief_fingerprint` pass for a whole sprint while the CLI printed nothing. |
| AC6 | in file_finding.py, make `is_derived_criterion` return True unconditionally - census 17 bugs/0 stories to 364/669. The round-1 row named removing `count=1`, which is behaviourally INERT: `_AC_NUMBER_RE` is `^`-anchored without MULTILINE, so `sub(count=0)` and `sub(count=1)` are identical for every input | Given the corpus, when the census is recomputed with the fix, then exactly 4 bugs flip to `derived-only` (BG0537, BG0547, BG0578, BG0581) and 0 stories - two seats measured this independently, and any other number means the fix over- or under-reaches. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | Round 1 REJECT repaired. The code fix was found correct; the EVIDENCE was not. AC3's control was case-mismatched and its mutant survived 6603 tests; AC6's test resolved the repo root to `.claude/` so it measured nothing, and asserted no count; AC6's declared mutant was inert; AC5 named `plan` and ran `breakdown`, asserting no refusal. Boundary cases (`AC power`, `ACL check`, `ACCEPT:`) and a positive control added |
