# BG0621: the release bar can report MET while a High is open: severity is matched case-sensitively, only the literal status Open counts, and a hyphenated heading skips the file entirely

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 9; plan rows 9; executed 9; killed 9; survived 0; not-run 0; entry point 6 of 9 criteria through the shipped CLI, 3 in-process | fp 3a356252f860 ]] (nine criteria over the two population readers, each with its own mutant executed and killed: the case-insensitive match, the not-terminal status test, the widened heading, the unparseable report, the severity-and-status guards, the page reader left behind, and the report dropped from the bar path. Four are refusals, one is the paired control that keeps the bar able to PASS, one covers the second reader in the same file, one is measured against the live corpus rather than a fixture - which is how BG0131 was found - and the last two came from the review: a hand-copied vocabulary that can only drift, and a warning that fired at the release boundary but not on the per-commit path)
> **Points:** 2
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, sdlc-studio/bugs/BG0131-the-subagent-token-metric-does-not-track-work.md
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

- [x] **AC1** Given an open bug whose Severity is written `high` in any casing, when the release bar is read, then it is BARRED - the corpus already holds 7 such bugs, and a bar that reads a field the filer does not normalise is one whose answer depends on how somebody typed
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_severity_is_matched_regardless_of_casing
  - **Verified:** yes (2026-08-26)
- [x] **AC2** Given a bug at High whose Status is any NON-TERMINAL state, when the bar is read, then it is BARRED - `In Progress` is a legitimate bug status and the resting state of every High this run will touch, and `Blocked`, which is NOT in the bug vocabulary at all, must fall OPEN too, so a typo or a project-declared status over-refuses rather than hides
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_every_non_terminal_status_counts_as_open
  - **Verified:** yes (2026-08-26)
- [x] **AC3** Given a bug at High whose H1 reads `# BG-0123:` with the hyphenated id form, when the bar is read, then it is BARRED - 21 files in this corpus use that form and each is currently skipped in full, taking its status and severity with it
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_a_hyphenated_heading_is_still_read
  - **Verified:** yes (2026-08-26)
- [x] **AC4** Given a bug file matching NONE of the expected patterns, when the bar is read, then it is REPORTED by path rather than skipped - a finding the bar cannot parse is the one case where silence and a clean bill of health are indistinguishable, and that is what all three hatches have in common
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_an_unparseable_finding_is_reported_not_dropped
  - **Verified:** yes (2026-08-26)
- [x] **AC5** Given a corpus whose open findings are all terminal or below the barred severities, when the bar is read, then it reports MET exactly as today - the paired control, so widening the population does not turn the bar into a check that can never pass
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_a_clean_corpus_still_reports_the_bar_met
  - **Verified:** yes (2026-08-26)
- [x] **AC6** Given the same three malformed findings, when the DISCLOSURE PAGE is generated, then each appears on it - the page's own population reader repeats all three guards verbatim, so repairing the bar alone would leave the defect standing in the same file it was found in
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_the_disclosure_page_reads_the_same_population_as_the_bar
  - **Verified:** yes (2026-08-26)
- [x] **AC7** Given the LIVE corpus, when the unparseable set is read, then it is EMPTY - and it was not before this fix: the guard's first execution surfaced BG0131, invisible to both readers since 2026-07-14 because its H1 carried a parenthetical between the id and the colon. This criterion is deliberately about the corpus rather than a fixture, because a guard whose first run over real data finds nothing has not been shown to look
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_the_live_corpus_has_no_unparseable_finding
  - **Verified:** yes (2026-08-26)
- [x] **AC8** Given a terminal status the shipped bug vocabulary gains later, when the release bar reads it, then the two agree - `TERMINAL` here is a hand-copy of what `sdlc_md` already owns, and a hand-copy can only drift. It drifts in the safe direction, over-refusing, which is exactly why nobody would ever connect the symptom to the cause
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_the_terminal_set_matches_the_shipped_bug_vocabulary
  - **Verified:** yes (2026-08-26)
- [x] **AC9** Given an unreadable finding, when `--check` runs - the per-commit path, not the release boundary - then it is NAMED, and `--check` still passes when the page itself agrees with the corpus. Warning only at the tag is how BG0131 sat unread from 2026-07-14
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_check_and_write_also_report_an_unreadable_finding
  - **Verified:** yes (2026-08-26)

## Impact

This is the checker a release tag is judged on, and the one the current sprint goal names as its success condition. A bar that can answer MET while a High is open is a gate failing open, and its green is not evidence until this lands - which is why it is delivered before anything else in the batch rather than alongside it.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `known_issues.py`, replace the case-insensitive severity match in `_matches` with a plain `in` against `BARRED`, as the shipped guard does | Given an open bug whose Severity is written `high` in any casing, when the release bar is read, then it is BARRED - the corpus already holds 7 such bugs, and a bar that reads a field the filer does not normalise is one whose answer depends on how somebody typed |
| AC2 | in `known_issues.py`, replace the not-terminal test in `_is_open` with the literal `== "Open"` the shipped guard uses | Given a bug at High whose Status is any NON-TERMINAL state, when the bar is read, then it is BARRED - `In Progress` is a legitimate bug status and the resting state of every High this run will touch, and `Blocked`, which is NOT in the bug vocabulary at all, must fall OPEN too, so a typo or a project-declared status over-refuses rather than hides |
| AC3 | in `known_issues.py`, narrow `_HEADING` back so a hyphenated id no longer matches | Given a bug at High whose H1 reads `# BG-0123:` with the hyphenated id form, when the bar is read, then it is BARRED - 21 files in this corpus use that form and each is currently skipped in full, taking its status and severity with it |
| AC4 | in `known_issues.py`, drop the unparseable report from the `--bar` path so an unreadable finding is skipped silently | Given a bug file matching NONE of the expected patterns, when the bar is read, then it is REPORTED by path rather than skipped - a finding the bar cannot parse is the one case where silence and a clean bill of health are indistinguishable, and that is what all three hatches have in common |
| AC5 | in `known_issues.py`, delete the severity and status guards from `barred_open`, so every finding is returned as barred whatever it says | Given a corpus whose open findings are all terminal or below the barred severities, when the bar is read, then it reports MET exactly as today - the paired control, so widening the population does not turn the bar into a check that can never pass |
| AC6 | in `known_issues.py`, narrow the page's population reader back to the old three guards while the bar keeps the new ones | Given the same three malformed findings, when the DISCLOSURE PAGE is generated, then each appears on it - the page's own population reader repeats all three guards verbatim, so repairing the bar alone would leave the defect standing in the same file it was found in |
| AC7 | in `known_issues.py`, narrow `_HEADING` back so a hyphenated id no longer matches - the mutant is a HEADING change and not a `--bar` change, because this criterion's test reads the corpus in-process and never calls `main` | Given the LIVE corpus, when the unparseable set is read, then it is EMPTY - and it was not before this fix: the guard's first execution surfaced BG0131, invisible to both readers since 2026-07-14 because its H1 carried a parenthetical between the id and the colon. This criterion is deliberately about the corpus rather than a fixture, because a guard whose first run over real data finds nothing has not been shown to look |
| AC8 | in `known_issues.py`, add a status to `TERMINAL` that the shipped bug vocabulary does not carry, so the hand-copy drifts | Given a terminal status the shipped bug vocabulary gains later, when the release bar reads it, then the two agree - `TERMINAL` here is a hand-copy of what `sdlc_md` already owns, and a hand-copy can only drift. It drifts in the safe direction, over-refusing, which is exactly why nobody would ever connect the symptom to the cause |
| AC9 | in `known_issues.py`, delete the `_warn_unparseable` call from the check and write path, leaving the report on `--bar` alone | Given an unreadable finding, when `--check` runs - the per-commit path, not the release boundary - then it is NAMED, and `--check` still passes when the page itself agrees with the corpus. Warning only at the tag is how BG0131 sat unread from 2026-07-14 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
