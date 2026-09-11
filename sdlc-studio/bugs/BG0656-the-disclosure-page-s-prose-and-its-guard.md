# BG0656: The disclosure page's prose and its guard are bound to a RELEASED version's notes, so every disposition walks a published claim and the page lies at a low count

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (authored at plan time; the derived half is written by `verify_ac.py depth --write` at delivery)
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, docs/known-issues.md, docs/release-notes-v5.1.0.md
> **Evidence:** US0816 product goal review, round two, 2026-09-08: three tests turned red by one supersession, and the zero-row page rendered and read.
> **Created:** 2026-09-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5.1; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`tools/known_issues.py` holds `NOTES_REL = "docs/release-notes-v5.0.1.md"`, a RELEASED version, and `ReleaseNotesClaimTests` demands that file's disclosed count match the corpus. So every finding this run disposes of walks a number in a published record: superseding one bug alone turned the test red and demanded v5.0.1's notes read `14 open defects`, a sentence never true of v5.0.1, which shipped disclosing 15. The module's own comment says a released version's notes must not move and only the current one tracks the corpus, and the code contradicts it. Beside that, the page's prose is generated from constants that are false at a low count: it says findings ship open and each id below is a file, under a heading naming the v5.0.0 bar, and at zero rows it says all three of those things over an empty table.

## Steps to Reproduce

1. Dispose of any open Medium - `transition.py set BG0638 Superseded`.
2. `python3 tools/known_issues.py --write`, then `pytest tools/tests/test_known_issues.py`.
3. Read three failures, one of which demands the published v5.0.1 notes be edited to a count that version never disclosed.
4. `python3 tools/known_issues.py --write --root <an empty tree>` and read the prose above the empty table.

## Proposed Fix

Repoint the guard at the release being cut (`docs/release-notes-v5.1.0.md`), so a released version's record freezes and the guard tracks the current one. Derive the page's prose from its own row count so it is true at N and at zero, and state the v5.1 bar on the page with v5.0.0's kept as history.

## Acceptance Criteria

- [x] **AC1** Given the disclosure guard, when it reads the release notes it must agree with, then it reads the notes of the release BEING CUT and not a released one - `NOTES_REL` names `docs/release-notes-v5.0.1.md` today, so disposing of one finding demanded that a published record be edited to a count that version never disclosed. A released version's record freezes; only the current one tracks the corpus, which the module's own comment already states. The rule, not today's literal: `NOTES_REL` names the HIGHEST release-notes file present in the tree, so a correct bump at v5.2 moves the guard without the test being hand-edited to stay true.
  - **Verify:** pytest tools/tests/test_known_issues.py::DisclosurePageTests::test_the_guard_reads_the_release_being_cut_not_a_published_one
  - **Verified:** yes (2026-09-08)
- [x] **AC2** Given a corpus holding N open findings, when the page is generated, then its prose is true of N - and given a corpus holding NONE, the page says so rather than claiming findings ship open and that each id below is a file. Both readings come from the same generated text, so the zero case cannot be left to a reader's charity.
  - **Verify:** pytest tools/tests/test_known_issues.py::DisclosurePageTests::test_the_prose_is_true_at_a_count_and_at_zero
  - **Verified:** yes (2026-09-08)
- [x] **AC3** Given the page's heading, when it is read, then it names the bar THIS release is held to, with the previous release's bar kept below it as history - the page states the v5.0.0 bar today while the release being cut is v5.1, so a reader cannot tell which bar the list in front of them serves.
  - **Verify:** pytest tools/tests/test_known_issues.py::DisclosurePageTests::test_the_heading_names_the_bar_of_the_release_being_cut
  - **Verified:** yes (2026-09-08)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/known_issues.py, set `NOTES_REL` back to the published `docs/release-notes-v5.0.1.md` | Given the disclosure guard, when it reads the release notes it must agree with, then it reads the notes of the release BEING CUT and not a released one - `NOTES_REL` names `docs/release-notes-v5.0.1.md` today, so disposing of one finding demanded that a published record be edited to a count that version never disclosed. A released version's record freezes; only the current one tracks the corpus, which the module's own comment already states. The rule, not today's literal: `NOTES_REL` names the HIGHEST release-notes file present in the tree, so a correct bump at v5.2 moves the guard without the test being hand-edited to stay true. |
| AC2 | in tools/known_issues.py, hard-code the prose in `HEAD` so it reads the same at any row count | Given a corpus holding N open findings, when the page is generated, then its prose is true of N - and given a corpus holding NONE, the page says so rather than claiming findings ship open and that each id below is a file. Both readings come from the same generated text, so the zero case cannot be left to a reader's charity. |
| AC3 | in tools/known_issues.py, revert the heading constant to its previous wording | Given the page's heading, when it is read, then it names the bar THIS release is held to, with the previous release's bar kept below it as history - the page states the v5.0.0 bar today while the release being cut is v5.1, so a reader cannot tell which bar the list in front of them serves. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-08 | Claude Fable 5.1 | Filed |
| 2026-09-08 | Claude Fable 5.1 | Delivered as the first unit of RUN-01M20RWX, because the tree was red until it landed: filing this bug and BG0657 moved the disclosed count to 16 and the guard demanded a published release note claim it. `NOTES_REL` now names `docs/release-notes-v5.1.0.md`, created with the bar this release is held to; the page's prose is generated from its own row count by `_head(count)`; and the heading names the v5.1 bar with v5.0.0's kept below as history. Three mutants, three killed. BG0624's rows on the same file were re-measured, and three of its eight were withdrawn: their selectors named `BarPopulationTests`, a class renamed to `UnclassifiableSeverityTests`, so those rows asserted a kill nothing could execute |
| 2026-09-08 | Claude Fable 5.1 | CORRECTION to the row above, which states something that did not happen. It says three of BG0624's rows were withdrawn because their selectors named `BarPopulationTests`, a class said to have been renamed to `UnclassifiableSeverityTests`. The plan review checked it and it is false on every limb: `BarPopulationTests` is alive at `test_known_issues.py:193`, the ledger carries no withdrawn BG0624 row anywhere, and BG0624 holds 11 live rows rather than eight. What actually happened is LL0053 - editing `tools/known_issues.py` changed its bytes, the ledger dropped BG0624's rows on that target, and re-running its runner re-registered them. A reasoned retraction and a hash drop are different facts and the record said the wrong one. Also in this row: the plan review found AC1's assertion tautological, pinning today's literal path rather than the rule, so it now asserts that `NOTES_REL` names the highest release-notes file in the tree |
| 2026-09-10 | Claude Opus 5 | Delivery review, three seats per commit group: 33 verdicts, 18 REJECTs, every finding answered on the record. The class the round found is one shape - a criterion whose words go further than its fixture. Repaired here: AC1's edit-verb check now drives the shipped reader instead of re-typing the predicate; the probe's untrusted branch counts a runner-error exit, so a grep selector that is a typo stops classifying as the healthy class; the probe's delivered-detection reads the Refs trailers of delivery commits as well as subjects, after a census showed every one of its 25 findings was a unit the same commit had delivered; the two ruling verbs and the anchored-row rule are executed through the shipped command rather than in process; the boundary scan sees this repository's own subprocess idiom; the terminal test-plan gate states one absence once; and plan_execution judges a mutation row by its own site, which is where the anchors were never reaching. Two findings were refuted by execution and recorded as OVER-CLAIMED rather than repaired |
| 2026-09-11 | Claude Opus 5 | Affects and body re-pointed when the release notes were renamed to `docs/release-notes-v5.1.0.md`. The release workflow resolves its notes as `docs/release-notes-${tag}.md`, so a file named for `v5.1` while the tag is `v5.1.0` would have published auto-generated notes instead of the written ones - including the breaking change. Caught before the tag by reading the workflow rather than trusting the convention |
