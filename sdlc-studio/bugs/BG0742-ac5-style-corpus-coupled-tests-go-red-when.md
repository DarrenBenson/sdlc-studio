# BG0742: AC5-style corpus-coupled tests go red when the backlog they measure is acted on, and two are red in this tree already

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/workspace.py
> **Evidence:** Raised by the independent engineering seat during BG0722's review, 2026-09-22, which both defended the instrument and asked that the cost be filed. It also identified the pre-existing red test as corroboration that this coupling bites in practice.
> **Created:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0722's AC5 asserts the `abandoned` lens reports a non-zero count against this repository's real backlog, because its predecessor was correct on fixtures and reported zero here. That instrument is right and it has a cost: it goes red the moment the three requests it names are closed or their children touched, which is the stated purpose of the sweep that raised the bug. The reviewer dated the window - CR0555 reaches 45 days on 2026-10-09 and CR0507/CR0556 on 2026-10-11 - so acting on the findings opens roughly 17 days of red before the test self-heals. It is not hypothetical: `test_sprint.py::RungTerminalAndProductTests::test_the_build_rung_still_reports_its_own_terminal` is red in this tree right now from the same coupling.

## Steps to Reproduce

1. Act on CR0424, CR0441 or CR0512 - close them or touch their children.
2. Run the module: AC5's test reports zero and fails.
3. Nothing in the tree has regressed; the backlog simply improved.

## Proposed Fix

Replace each assertion over the live backlog (`test_backlog_triage`'s `test_the_lens_is_not_inert_against_the_real_corpus`, and the derived-only census BG0732 raised) with the same assertion over a fixture of verbatim copies of the artefacts that exposed the defect, dated against a fixed today, keeping the test names so BG0722's and BG0585's stamps still resolve. Add no expectation file or count (a hand-kept pin, LC-008).

## Acceptance Criteria

- [ ] **AC1** Given `test_backlog_triage`'s abandoned-lens and duplicate assertions, when they run, then they read a fixture of verbatim copies of the artefacts that exposed BG0722 and BG0585, dated against a fixed today, not the live backlog; and making the lens return nothing still turns them red.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::AbandonedRequestLensTests
- [ ] **AC2** Given the live backlog's abandoned CR0424, CR0441 and CR0512 and the US0793/US0794 duplicate are disposed of, when the suite runs, then `test_backlog_triage` and the derived-only census BG0732 raised stay green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::DuplicateLensTests
- [ ] **AC3** Given the change, then no expectation file, recorded count or other hand-kept pin is added, and the test names BG0722's and BG0585's stamps cite still resolve.
  - **Verify:** manual - the reviewer confirms the diff adds no expectation file, recorded count or hand-kept pin

## Impact

A green suite is the signal every gate in this repository depends on, and a test that fails because the work it measures was DONE trains a reader to ignore it. The alternative - proving a detector on a fixture alone - is the inert-mechanism failure this project has paid for repeatedly, so the instrument should be kept and its cost managed rather than removed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | Claude Opus 5 | A SECOND instance surfaced the same day, and one of its two forms is now fixed. `test_file_finding.DerivedDetectorSeesItsOwnWriterTests::test_the_corpus_census_stays_within_its_measured_bounds` asserted an ABSOLUTE count of bugs reading derived-only, ceiling 60, to catch the pattern OVER-REACHING. It breached on the very run that filed this finding: 53 before that run's seven filings, 60 after, with `conformance.py` untouched. That is backlog volume, not over-reach. It is now a RATIO with a 15% ceiling - currently 8.1% - which falls as findings are groomed and still kills the over-reach mutant the test names (verified by making `unit_is_ungroomed` always answer derived-only). The remedy this bug proposes is the general form of that: measure the property, not the corpus. BG0722's AC5 is still the absolute-count shape and still needs it. |
| 2026-09-22 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Proposed fix reworded at Sprint 3 planning from measurement: the previous fix was refuted or would add a hand-kept pin (LC-008) |
