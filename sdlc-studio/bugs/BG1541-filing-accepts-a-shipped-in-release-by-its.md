# BG1541: Filing accepts a Shipped-in release by its CHANGELOG heading that escape.py trace then refuses as not a git tag

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py, .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, stories lens, survived 3 of 3 refute votes; observed at sdlc-studio/stories/US1157-a-bug-records-that-it-escaped-to-production.md AC2 ('a `--shipped-in` naming no tag or release in the project') against US1158 AC1/AC3; .claude/skills/sdlc-studio/scripts/file_finding.py:1775-1781 and 1811-1815; .claude/skills/sdlc-studio/scripts/escape.py:60-66 and 163-169
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:13Z

## Summary

The two halves of the escape record define a release differently. Filing a bug with `--escaped` and `--shipped-in` goes through `release_resolves` in `file_finding.py`, which accepts a git tag or a CHANGELOG.md heading of that version, with or without the leading `v`. The trace in escape.py reads only an exact git tag of that name and exits 2 otherwise. A bug filed as shipped in 6.4.0 is therefore stored as a valid escape record and can never be traced, because the tag is spelt v6.4.0. A smaller split of the same kind sits on `--escaped-via`: filing accepts any story or bug on disk, while the trace's confirm step refuses a unit that the commits of that one release do not name. No criterion in US1157 or US1158 exercises the other story's definition, so neither test suite sees it.

## Steps to Reproduce

1. In this repository, where the tag is v6.4.0 and CHANGELOG.md carries a heading for [6.4.0], call `release_resolves` in `file_finding.py` with the name 6.4.0. It returns True, so a bug filed with --escaped and --shipped-in 6.4.0 is accepted and written with Shipped-in 6.4.0.
2. Call `release_units` in escape.py with the same name 6.4.0, or run escape.py trace on the bug filed in step 1.
3. Observed: the trace refuses with the message that release 6.4.0 is not a git tag in this project and nothing is proposed, exit 2.
4. Expected: a release name that filing accepts is one the trace can read, or filing refuses it.
5. Positive control: the same two calls with v6.4.0 both succeed.

## Proposed Fix

Give both scripts one resolver. Add a function that turns a release name into the git tag it means (the exact tag, else the same name with or without a leading `v`), and have `check_escape` in `file_finding.py` store the resolved tag spelling in Shipped-in while `release_units` in escape.py resolves through the same function before reading the span. A name that matches only a CHANGELOG heading with no tag behind it is refused at filing with a message saying the trace needs a tag. For `--escaped-via`, either state in the filing help and reference-scripts-review.md that the confirm step accepts only a unit the named release shipped, or have filing print a note when the named unit is not in that release's span. Pin both with a test that files against the changelog spelling of a tagged release and then traces it.

## Acceptance Criteria

- [ ] **AC1** Given a project tagged v6.4.0 whose CHANGELOG.md carries a [6.4.0] heading, when a bug is filed with `--escaped --shipped-in 6.4.0` and `escape.py trace` is then run on it, then the bug's Shipped-in holds the tag spelling v6.4.0 and the trace reads the release instead of exiting 2. Fails on: filing storing a release name the trace refuses as not a git tag.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceTests::test_a_bug_filed_by_the_changelog_spelling_of_a_tag_is_traced
- [ ] **AC2** Given a version that has a CHANGELOG.md heading and no git tag in either spelling, when a bug is filed with `--escaped --shipped-in` naming it, then filing refuses, saying the trace needs a tag, and writes nothing; the same filing against a tagged version is accepted. Fails on: an escape record stored that can never be traced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py::BugEscapeFieldTests::test_a_changelog_heading_with_no_tag_behind_it_is_refused
- [ ] **AC3** Given `--escaped-via` naming a story or bug on disk that the commits of the named release do not ship, when the bug is filed, then the filer prints a note naming the unit and the release, or its help and `reference-scripts-review.md` state that the trace's confirm step accepts only a unit that release shipped. Fails on: filing accepting silently a unit the confirm step will refuse, with the rule written nowhere.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::EscapedViaOutsideTheReleaseTests::test_a_unit_the_release_did_not_ship_is_not_accepted_silently

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
