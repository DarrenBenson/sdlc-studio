# BG0502: a close sealed by --file-and-close tells the operator nothing, because cmd_close returns before the report

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Found by the round-four independent pass on US0604 during the RUN-01KYZKY5 close, reproduced live in a fixture.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** closing review RUN-01KYZKY5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The close report is emitted from two places: `cmd_close`'s success path and the --apply-signoff tail. The --file-and-close route returns before both, so a run sealed `closed-outstanding` prints no CLOSE REPORT at all. That is the route taken when a close is BLOCKED and its ceremony debt is filed and deferred, which is precisely the case where the operator most needs an account of what shipped, what is carried and what was deferred.

## Steps to Reproduce

Drive a close whose blockers are all deferrable to `sprint.py close --file-and-close --retro RETROxxxx` and read stdout: the filing summary appears, no CLOSE REPORT does.

## Proposed Fix

Emit the report on that route too, before the bounded-exit return, and pin it with a criterion driven through the command. Decide whether a `closed-outstanding` report should name the deferrals in its own section.

## Acceptance Criteria

- [x] **AC1: the bounded exit prints the close report, naming what was deferred.**
  - **Given** a close whose blockers are all deferrable, sealed with `--file-and-close`
  - **When** it is driven through `main(["close", ...])`
  - **Then** stdout carries the CLOSE REPORT with a DEFERRED section naming each filed artefact,
    and the wording distinguishes deferred from waived
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseTests::test_file_and_close_prints_the_close_report_naming_the_deferrals
  - **Verified:** yes (2026-08-03)

- [x] **AC2: an ordinary close carries no DEFERRED section.**
  - **Given** a close that deferred nothing
  - **When** the report is built
  - **Then** the section is absent rather than reading "none deferred" - a section that appears
    on every close trains the eye past it, and this is the line that matters on the one route
    where it is ever non-empty
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseTests::test_an_ordinary_close_report_carries_no_deferred_section
  - **Verified:** yes (2026-08-03)

## Verification evidence

Functional, driven through `main(["close", "--file-and-close", ...])`. A criterion calling
`_tell_the_operator` directly is green whether or not this route reaches it, which is how the
gap survived US0604's five criteria - so the test drives the command.

| Mutant | Result |
| --- | --- |
| remove the `_tell_the_operator` call from the `--file-and-close` route | killed by AC1 |
| always emit the DEFERRED section | killed by AC2 |

**The decision this bug asked for.** A `closed-outstanding` report DOES name its deferrals, in
its own section, marked "filed, not waived" - the same distinction the retro and the review
anchor already carry, repeated here because the report is what the operator actually reads.

## Round 2: what the independent review rejected, and what changed

REJECTed at the lane boundary with two blocking findings.

**The footprint was understated.** `sprint_report.py` holds the whole DEFERRED section and is
the exact target of AC2's Verify command, and neither this unit nor its sibling BG0499 declared
it. That is not bookkeeping: `critic.py brief` bounds the review diff to the declared `Affects`,
so the reviewer was handed a scope omitting the file implementing the criterion they were told
was law - and said so. Declared now.

**AC1's own words were not pinned.** The criterion says the section NAMES each filed artefact;
the test asserted only that a DEFERRED heading and the phrase "not waived" appeared. Two mutants
therefore SURVIVED in review: a summary line carrying no id at all, and a payload holding just
the first of two filings. The test now reads the ids the fixture actually filed off disk and
asserts each one appears inside the DEFERRED block - compared with the hyphen stripped, because
an id is written `CR-0001` for a reader and `CR0001` in a filename and both are the same id.
Both surviving mutants were re-applied with the syntax checked and are now killed.

The non-blocking prose finding is fixed too: the changelog quoted the marker as "filed, not
waived" where the retro and anchor read "(deferred, not waived)". Same distinction, and the
fragment now quotes both accurately.

## Impact

The one exit designed for a close that could not complete cleanly is the one that reports least.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | closing review RUN-01KYZKY5 | Filed |
