# BG0504: seven repo guards read the live index directly, so taking reconcile's own archival advice turns the tree red

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** tools/tests/test_epic_index_derived.py, tools/tests/test_supersession_records.py
> **Verification depth:** functional
> **Evidence:** Hit while running the archival sweep advised by reconcile against HEAD 4979f93f on 2026-08-03, after filing BG0503. Five types archived to v5.0.0 (472 story, 271 cr, 178 bug, 177 epic, 55 rfc); the commit-msg suite lane refused with 7 failures, captured in sdlc-studio/.local/gate-suite-last.log.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`reconcile detect` advises archiving on every run once a live index passes `indexes.archive_after`. Taking that advice - `archive.py archive --type epic|rfc --release v5.0.0`, the exact command the advisory prints - reddens seven guards under `tools/tests/`, and the commit is refused.

Both guards read `sdlc-studio/<type>/_index.md` with a bare `read_text` and treat what they find as the whole corpus. The machinery already knows better: `reconcile.parse_index` unions the live rows with every `<type>/archive/**/*.md` sub-index row precisely so an archived artefact is still seen as in the index, and its docstring says so. The guards bypass it.

Four `test_epic_index_derived` failures are floor assertions calibrated to an unarchived index - `len(rows) > 150`, `checked > 150`, `absent > 100` - which read 30 once 177 epic rows moved. The floors are defending something real (a sweep that matches nothing passes exactly like a clean tree does), so the fix is the population, not the number. Three `test_supersession_records` failures look for RFC-0009's and RFC-0034's rows and find nothing, because both are archived; the guard then reports a supersession record as missing when it is present one file over.

The detectors under test are all fine. `epic_index_derivable_drift`, `epic_index_uncorroborated_advisory` and `reconcile detect` itself all returned correct results over the archived tree - only the tests' own reading of the corpus was stale.

## Steps to Reproduce

From a clean tree, run `reconcile.py --root . detect` and read the five archival advisories. Take one: `archive.py --root . archive --type rfc --release v5.0.0`. Then run `python3 -m unittest discover -s tools/tests`: 7 failures across the two files, none of which reflect a defect in the subject under test.

## Proposed Fix

Read the corpus as live UNION archive in both guards, the same union `reconcile.parse_index` performs, so the population is whatever exists rather than whatever has not been archived yet. The floors then hold their original meaning and survive the next sweep. Pin it with a criterion that archives a type inside a copied tree and asserts the guard still passes - a floor that silently tracks the live table is the mutant this class needs to fail on.

## Acceptance Criteria

- [x] **AC1: both guards read the live index unioned with its archive sub-indexes, and all seven pass over the archived tree.**
  - **Verify:** `python3 -m unittest discover -s tools/tests -p "test_epic_index_derived.py"` and `-p "test_supersession_records.py"`
  - **Verified:** yes (2026-08-03) - 7 and 4 tests, both OK, against the tree with all five types archived to v5.0.0

- [x] **AC2: a guard reverted to a live-only read fails.**
  - **Verify:** replace `_index_rows`'s path list with `[repo / rel / "_index.md"]`, purge `__pycache__`, re-run under `python3 -B`
  - **Verified:** yes (2026-08-03) - mutant killed by 5 of the 7 tests (10 failures), including the new
    `test_the_sweep_reads_archived_rows_and_not_only_the_live_table`; source restored and re-run green

- [x] **AC3: the recorded uncorroborated counts are pinned wherever the row now lives.**
  - **Given** archiving moves a row without changing it, and the advisory's scope is the live table `apply` rewrites
  - **Then** the advisory is compared against the live subset, and the six recorded numbers are asserted over the whole corpus, so an archived row that lost its value still fails
  - **Verify:** `python3 -m unittest discover -s tools/tests -p "test_epic_index_derived.py"` - `test_the_uncorroborated_rows_are_ADVISORY_and_untouched`
  - **Verified:** yes (2026-08-03)

**Narrowed from the filing.** The proposed fix asked for a criterion that archives a type inside a copied
tree. What shipped asserts the same property against the real corpus, which is already archived: the union
must find rows the live table does not hold. It kills the same mutant without standing up a second archival
fixture whose drift from the shipped `archive.py` would be its own defect.

## Verification evidence

Functional. Both guard suites executed over the archived tree, and the live-only mutant executed and killed
with the source restored byte-identical (`git diff` clean on the restore). Not run: the full repo suite,
which the commit gate runs.

## Impact

The one maintenance operation the tooling advises on every reconcile run cannot be performed without breaking the gate. The advisories have been printing for long enough that five indexes reached 6-15x their threshold, and this is why: whoever tried it last hit a red suite with no obvious connection to what they had done. An agent reading only the failures would conclude the epic index or the supersession record was corrupt, and repair the wrong thing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
