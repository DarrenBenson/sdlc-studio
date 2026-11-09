# BG1312: The resume brief's known-issues scan matches only a `Raised-in-batch` stamp naming the run id, so a brief written mid-run says no known issues while findings filed during the run are open

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/resume_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py, changelog.d/BG1312.md
> **Evidence:** US1140-verdict-r1 findings 1-2 (RUN-01M7061X); file_finding.py:2320-2327 writes the moment stamp mid-run
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T13:59:18Z

## Summary

From US1140's QA review (qa-seat-US1140-r1, non-blocking findings 1 and 2, 2026-11-09). `lib/resume_brief.py` lists a run's known issues by matching a `Raised-in-batch` stamp that names the run id. `file_finding` names the run only when the close files for it; every finding filed while a run is open is stamped `none open - raised outside a delivery batch, <moment>`, and `sprint_report` and `close_owed` place it in the run by that moment. On a scratch copy of RUN-01M7061X the brief says 'none' while BG1309, BG1310 and BG1311, all filed inside the run's window, are open. US1140's fixtures use stamp shapes no tool writes mid-run, so its tests pass. A fresh session resuming from the brief loses the run's known issues, which CR0670's hand-off exists to carry.

## Steps to Reproduce

1. Open a run and file a bug with `file_finding.py file` while it is open.
2. Build the resume brief for the run with `resume_brief.build`.
3. Its known-issues section says none, though the bug is open and was filed inside the run's window.

## Proposed Fix

Place a finding in the run the way `sprint_report` does: by the moment carried as the stamp's last token, inside the run's start and end, as well as by a stamp naming the run; read it through the helper `sprint_report` uses rather than a second parser. Give the fixtures the stamp `file_finding` actually writes mid-run, and add a test that a finding filed mid-run is listed while one filed before the run starts is not.

## Acceptance Criteria

- [ ] **AC1** Given an open run and a bug filed with `file_finding.py file` while it is open (so stamped `none open - raised outside a delivery batch, <moment>` with a moment inside the run's start and end), when `resume_brief.build` renders the brief, then its known-issues section names that bug. Fails on: the section saying none while such a bug is open.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::KnownIssuesTests::test_a_finding_filed_mid_run_is_listed_by_its_moment
  - **Verified:** yes (2026-11-09)
- [ ] **AC2** Given the same run, then a bug whose stamp's moment falls before the run's start, and a bug already Fixed, are both left out of the known-issues section, while a bug whose stamp names the run id is still listed. Fails on: a pre-run or closed finding listed; a run-id stamp no longer matched.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::KnownIssuesTests::test_pre_run_and_closed_findings_are_left_out_and_a_run_stamp_still_matches
  - **Verified:** yes (2026-11-09)
- [ ] **AC3** Given `lib/resume_brief.py`, then it reads a finding's moment through the helper `sprint_report` uses to place a finding in a run, not a second parser of the stamp, and the fixtures in `test_resume_brief.py` use the stamp shape `file_finding` writes mid-run. Fails on: a second stamp regex in resume_brief.py; a fixture stamp no tool writes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::KnownIssuesTests::test_the_moment_is_read_through_the_report_helper
  - **Verified:** yes (2026-11-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-09 | Claude Opus 5.5 (run nine, D0448) | Criteria and Verify lines authored when BG1312 joined the run |
