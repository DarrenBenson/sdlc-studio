# BG0621: the release bar can report MET while a High is open: severity is matched case-sensitively, only the literal status Open counts, and a hyphenated heading skips the file entirely

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py
> **Evidence:** Found by the pre-code goal review of the zero-open-High batch, 2026-08-26, and confirmed independently by the authoring session: guards quoted from tools/known_issues.py:112-130 per D0151, and the corpus counts taken by grep over sdlc-studio/bugs/. The same measurement established that no non-terminal High escapes the bar today, so all three are latent rather than active.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`known_issues.py barred_open` (tools/`known_issues.py`:112-130) decides the release bar and has three ways to miss an open High. First, `if severity.group(1).strip() in BARRED` where `BARRED = ("Critical", "High")` is a case-sensitive tuple - the corpus holds 7 bugs written `Severity: high`, plus 10 `medium`, 4 `low` and one `major`, because `file_finding.py` does not normalise the field. Second, `if status.group(1).strip() != "Open": continue` - only the literal `Open` counts, so a High at `In Progress` is invisible to the bar although `In Progress` is a legitimate member of the bug vocabulary and is the resting state of a bug somebody is halfway through fixing. Third, `_HEADING = re.compile(r"^# (BG\d+): (.+)$")` combined with `if not (status and severity and heading): continue` - a file whose H1 reads `# BG-0123:` fails the match and is skipped ENTIRELY, and 21 files in this corpus use exactly that form. Measured 2026-08-26: no non-terminal High or Critical escapes the bar TODAY, so all three are latent - but the status hatch becomes active inside any run that repairs a High, because the bug passes through `In Progress` on its way to Fixed.

## Steps to Reproduce

1. Set a bug to `Severity: high` (lowercase), or `Status: In Progress` at High, or give it an H1 of the form `# BG-0123:`. 2. `python3 tools/known_issues.py --bar`. 3. It prints `release bar met` and exits 0 with that bug open. Confirmed by reading the three guards at tools/`known_issues.py`:112-130 and by counting the corpus: 7 lowercase `high`, 21 hyphenated headings.

## Proposed Fix

Normalise before comparing, and define open as NOT-TERMINAL rather than as one literal string. Severity should be compared case-insensitively against the barred set. Status should be read through the type's own vocabulary and treated as open unless it is terminal, so every non-terminal state is caught rather than one enumerated state - the enumeration is the defect, and LL0043 records that an enumeration of a rule is a lower bound rather than a boundary. The heading pattern should accept the hyphenated id form the corpus already contains. A file that matches none of the three patterns must be REPORTED rather than skipped: silently dropping an unparseable finding from the release bar is the failure mode all three hatches share.

## Acceptance Criteria

- [ ] **AC1** Given an open bug whose Severity is written `high` in any casing, when the release bar is read, then it is BARRED - the corpus already holds 7 such bugs, and a bar that reads a field the filer does not normalise is one whose answer depends on how somebody typed
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_severity_is_matched_regardless_of_casing
- [ ] **AC2** Given an open bug at High whose Status is any NON-TERMINAL state - `In Progress`, `Blocked` - when the bar is read, then it is BARRED, because a bug being repaired is not a bug that is fixed, and `In Progress` is the resting state of every High this run will touch
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_every_non_terminal_status_counts_as_open
- [ ] **AC3** Given a bug at High whose H1 reads `# BG-0123:` with the hyphenated id form, when the bar is read, then it is BARRED - 21 files in this corpus use that form and each is currently skipped in full, taking its status and severity with it
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_a_hyphenated_heading_is_still_read
- [ ] **AC4** Given a bug file matching NONE of the expected patterns, when the bar is read, then it is REPORTED by path rather than skipped - a finding the bar cannot parse is the one case where silence and a clean bill of health are indistinguishable, and that is what all three hatches have in common
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_an_unparseable_finding_is_reported_not_dropped
- [ ] **AC5** Given a corpus whose open findings are all terminal or below the barred severities, when the bar is read, then it reports MET exactly as today - the paired control, so widening the population does not turn the bar into a check that can never pass
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_a_clean_corpus_still_reports_the_bar_met
- [ ] **AC6** Given the same three malformed findings, when the DISCLOSURE PAGE is generated, then each appears on it - the page's own population reader repeats all three guards verbatim, so repairing the bar alone would leave the defect standing in the same file it was found in
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_the_disclosure_page_reads_the_same_population_as_the_bar

## Impact

This is the checker a release tag is judged on, and the one the current sprint goal names as its success condition. A bar that can answer MET while a High is open is a gate failing open, and its green is not evidence until this lands - which is why it is delivered before anything else in the batch rather than alongside it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
