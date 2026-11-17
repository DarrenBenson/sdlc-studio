# US1233: The release cut writes a committed record of each release, with its date and the reports it shipped

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0695
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_record.py
> **Epic:** EP0339
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The release cut writes a committed record of each release, with its date and the reports it shipped
**So that** CR0695 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The cut writes a record naming the release, its date and its reports

- **Given** a project with a previous release tag, two sprint reports signed since it and one signed before it
- **When** the release is cut for a new version through `release_cut.py`
- **Then** a release record is written in the committed tree, outside `.local`, naming the version, the date of the cut and the two reports signed since the previous release, and not the earlier one. Fails on: every report on disk listed, a record with no date, or a record written where git ignores it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_the_cut_records_the_version_date_and_reports_since_the_last_release

### AC2: Cutting the same version again leaves one unchanged record

- **Given** a project whose release record for a version already exists
- **When** the cut is run again for that version on a later date
- **Then** there is still one record for the version and its date and report list are unchanged. Fails on: a second record for one release, or the date moved, either of which changes the count a failure rate divides by
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_a_second_cut_of_one_version_leaves_one_unchanged_record

### AC3: A release that shipped no signed report is still recorded

- **Given** a project with no earlier release and no signed sprint report
- **When** the first release is cut
- **Then** its record is written and states that it shipped no report, and the cut exits 0. Fails on: a crash or a skipped record, which would leave that release uncounted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_a_release_with_no_signed_report_is_still_recorded

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
