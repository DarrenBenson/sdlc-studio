# US1233: The release cut writes a committed record of each release, with its date and the reports it shipped

> **Status:** Done
> **Depends on:** -
> **Risk-class:** elevated
> **Delivers:** CR0695
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/scripts/tests/test_release_record.py, changelog.d/US1233.md
> **Epic:** EP0339
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who takes each release to the change board (Abena)
**I want** the release cut to write a committed record of each release: its version, the date of
the cut and the signed reports it shipped
**So that** a change failure rate has a count of releases to divide by, read from the committed
tree rather than from memory or the forge

## Context

### Background

D0458 ruled that a release is the deploy and that the release cut records each release, so
nobody records a deploy by hand. At HEAD `release_cut.py changelog-cut` writes CHANGELOG.md and
consumes the fragments, and nothing else: there is no record of a release to count. D0638 puts
this story before the 6.5.0 cut (US1330), so 6.5.0 is the first release with a record. US1234
reads the record to derive change failure rate.

---

## Acceptance Criteria

### AC1: the cut records the version, its date and the reports signed since the previous release

- **Given** a git project tagged `v1.0.0`, with RPT0001 signed before the tag's commit and RPT0002 and RPT0003 signed after it, and a CHANGELOG.md holding `## [Unreleased]` and one pending fragment
- **When** `release_cut.py changelog-cut --version 1.1.0` runs
- **Then** `sdlc-studio/reports/releases.jsonl` holds one line for 1.1.0 naming the date of the cut, the previous release `v1.0.0` and the reports RPT0002 and RPT0003 and not RPT0001, `git check-ignore` does not ignore the file, and the `[1.1.0]` section is cut as before. Fails on: HEAD, where the same cut changes only CHANGELOG.md and the consumed fragment (a fixture run on 2026-11-26 left `git status --short` listing CHANGELOG.md modified and changelog.d/US0001.md deleted, nothing else)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_the_cut_records_the_version_date_and_reports_since_the_last_release
- **Verified:** yes (2026-11-26)
- **Caller:** `release_cut.py changelog-cut`, which US1330 runs to cut 6.5.0; the record is read by `escape.py` (US1234's failure rate)

### AC2: a second cut of one version leaves one unchanged record

- **Given** a project whose 1.1.0 cut has written its record, after which the `[1.1.0]` section is taken back out of CHANGELOG.md (a cut that stopped before its section landed)
- **When** the cut is run again for 1.1.0 with the date a day later
- **Then** the record file still holds exactly one 1.1.0 line, byte-identical to the first, and the cut completes; and a cut refused because CHANGELOG.md already carries `[1.1.0]` leaves the record file byte-identical. Fails on: HEAD, whose first cut writes no record at all, so there is nothing to keep; or a second line, or a moved date, either of which changes the count a failure rate divides by
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_a_second_cut_of_one_version_leaves_one_unchanged_record
- **Verified:** yes (2026-11-26)
- **Caller:** `release_cut.py changelog-cut`, re-run by an operator after an interrupted cut

### AC3: a first release with no signed report, no tag and no git is still recorded

- **Given** a directory that is not a git repository and holds no `sdlc-studio/reports/` and no tag, as `test_release_cut.py`'s own cut fixtures are
- **When** the first release, 1.0.0, is cut
- **Then** the cut exits 0 and the record names 1.0.0 and the date, names no previous release and states that it shipped no signed report (an empty report list). Fails on: HEAD, which writes no record; or a cut that crashes or skips the record where git or the reports directory is absent, which would leave that release uncounted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_a_release_with_no_signed_report_is_still_recorded
- **Verified:** yes (2026-11-26)
- **Caller:** `release_cut.py changelog-cut` in a consuming project's first release

---

## Scope

### In Scope

- `changelog-cut` writes one record per version to `sdlc-studio/reports/releases.jsonl`
- The `release_cut.py` paragraph of `reference-scripts-domain.md` says the cut writes it

### Out of Scope

- Reading the record (US1234) and showing a rate (US1235)
- Back-filling records for releases cut before this story (6.4.0 and earlier have none; the 6.5.0 record names `v6.4.0` as its previous release)
- Any change to `tag-check` or the evidence pack

---

## Technical Notes

- Grounded at HEAD af477fc6d on 2026-11-26. `release_cut.py` has four verbs (`changelog-cut`, `record-green`, `tag-check`, `evidence-pack`) and no record of a release; the cut's date comes from `sdlc_md.now_date()` and lands only in the CHANGELOG heading.
- The record: one JSON object per line, `{"version", "date", "previous", "reports"}`, in `sdlc-studio/reports/releases.jsonl` beside the evidence packs. The path is fixed here because US1234 reads it and US1330's cut writes the first real line (6.5.0).
- The reports a release shipped: the signed reports no earlier record names, read through `sprint_report._signed_reports`, the reader the evidence page uses. For the first record in the file, the reports signed after the previous tag's commit (`git describe --tags --abbrev=0` from HEAD), or every signed report when there is no tag. So a report signed between a cut and its tag goes to the next release, never to none.
- Order: the CHANGELOG checks refuse before anything is written (BG1544, `test_a_refused_second_cut_leaves_the_changelog_and_fragments_untouched`), and the record write keeps that: a refused cut writes no record. A re-run that finds a record for its version keeps it as it is.
- Store `version` as given (`6.5.0`) and `previous` in the tag's own spelling (`v6.4.0`). US1234 treats `v1.1.0` and `1.1.0` as one release, as `escape.release_tag` does.
- `test_release_cut.py` calls `cut_changelog` in a plain temporary directory with no git, so the record write must not need git (AC3).
- New test module carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/release_cut.py` and drives the shipped CLI as a subprocess under `gitutil.git_env()`, as `test_release_cut._cli` does. A signed report fixture needs only `report_id` and a `signature` with `principal` and `signed_at`.
- Run twenty-eight: no other unit edits `release_cut.py`; US1294 also edits `reference-scripts-domain.md` and follows this story.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| The record file holds an unparsable line | The cut refuses before anything is written, naming the line (fail loud, LL0008) |
| The record file holds lines for other versions | They are left byte-identical; the new line is appended |
| A report was signed after the cut but before the tag | It is named by the next release's record, not lost |
| `sdlc-studio/reports/` holds no signed report | The record names an empty report list (AC3) |
| A cut refused for an existing `[X.Y.Z]` section, or for no `[Unreleased]` | No record is written, as no CHANGELOG change is |
| The project has no tag and earlier records exist | The previous release is the newest earlier record |

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| US1330 | Downstream | Runs this cut for 6.5.0, so it must follow this story and name `sdlc-studio/reports/releases.jsonl` in its Affects | Ready |
| US1234 | Downstream | Reads the record | Draft |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Re-grounded against HEAD for run twenty-eight (D0638) |
