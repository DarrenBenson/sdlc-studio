# BG1770: US1233 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/scripts/tests/test_release_record.py, changelog.d/US1233.md, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T08:29:39Z

## Summary

US1233 was rejected at round 2, the review cap, by agent-a030922d58013bbe5 (qa), so it was carried as a known issue rather than reviewed again. Filed at Low rather than the carry's default Medium: the release bar (`review.blocking_priority`) bars Medium, and Low is the most severe level it allows. The findings still open: BLOCKING: [new] A renamed annotated tag makes the first record name a release that is no tag and lose the reports shipped since it: `_previous_tag` (release\_cut.py:87-95) takes `git describe --tags --abbrev=0 HEAD` output as a tag name, but for a tag whose ref differs from the tag object's own name (git warns "tag 'v1.0.0' is externally known as '1.0.0'", the state the usual rename `git tag v1.0.0 1.0.0` then `git tag -d 1.0.0` leaves), git 2.56.0 prints `1.0.0-1-g5bf57365914310f532c0c2f448dadde644f426b3`. The rev-parse of `refs/tags/<that>^{commit}` at release\_cut.py:110 then succeeds, because git reads the describe suffix as HEAD's sha, so the reports committed at HEAD count as already shipped. On a fixture with RPT0001 signed at the tag and RPT0002 signed and committed one commit after it, the cut exits 0 and records `"previous": "1.0.0-1-g5bf57365914310f532c0c2f448dadde644f426b3", "reports": []`, where the same fixture with an ordinary `v1.0.0` tag records `"previous": "v1.0.0", "reports": ["RPT0002"]`. The release's report is lost without a word, contrary to AC1's reports signed since the previous release and to changelog.d/US1233.md:7 "the nearest tag reachable from HEAD", and a re-cut keeps the wrong line byte for byte. No test covers a misnamed tag. Resolving the ref itself (for example `git show-ref --verify` of `refs/tags/<name>`, or listing tags merged into HEAD) would close it; RULINGS: Round-one findings. "The write order that keeps an interrupted cut counted is pinned by no test" CLOSED: `test_a_cut_stopped_after_its_first_write_leaves_the_release_recorded` fails on the CHANGELOG-first mutant, and still fails after I cut its stop condition to the record write alone or dropped its CHANGELOG assertion. "The report order the `_shipped_reports` docstring states" CLOSED: `test_the_shipped_reports_are_listed_oldest_signature_first` fails on the id-sorted mutant. "The refusal for a report unreadable at the previous tag's commit" CLOSED: `test_a_report_unreadable_at_the_previous_tag_refuses_the_cut` fails on the mutant dropping UnreadableRecord from the except, and on a second mutant that swallows it and reads no reports at the tag. With its exit-code and refusal assertions removed it no longer kills the first, so those two assertions are the pin, and both are present. "The blank-line skip in `_release_records` is pinned only for an empty line" CLOSED: `test_a_later_cut_appends_and_ships_only_the_reports_no_record_names` now carries a three-space line and fails on the `if not line:` mutant. The builder's UNVERIFIABLE ruling, a ValueError for a tag rev-parse cannot resolve, is accepted on trust. My probe found no state where that rev-parse fails, since for a misnamed tag it resolves the describe output instead, which is the finding above. The repair 2033d31dd changes only test\_release\_record.py, and the unit's four files are unchanged from 2033d31dd to main at 1ec5379aa. test\_release\_record.py and test\_release\_cut.py, with the raw-git and scrub-site sweeps, pass 66 tests. `verify_ac.py run --id US1233 --dry-run` gives ac=3 pass=3 fail=0. No 6.5.0 row exists in this repository: sdlc-studio/reports/releases.jsonl is absent and `git ls-files` lists none. This repository's v6.4.0 is an ordinary tag (`git describe` prints v6.4.0), so its 6.5.0 cut is unaffected by the finding. `tools/lint-style.sh` fails only on sdlc-studio/decisions.md:660 (D0646, "optimization"), a file outside this unit.

## Steps to Reproduce

1. Read the round 2 REJECT of US1233 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1233 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] A renamed annotated tag makes the first record name a release that is no tag and lose the reports shipped since it: `_previous_tag` (release\_cut.py:87-95) takes `git describe --tags --abbrev=0 HEAD` output as a tag name, but for a tag whose ref differs from the tag object's own name (git warns "tag 'v1.0.0' is externally known as '1.0.0'", the state the usual rename `git tag v1.0.0 1.0.0` then `git tag -d 1.0.0` leaves), git 2.56.0 prints `1.0.0-1-g5bf57365914310f532c0c2f448dadde644f426b3`. The rev-parse of `refs/tags/<that>^{commit}` at release\_cut.py:110 then succeeds, because git reads the describe suffix as HEAD's sha, so the reports committed at HEAD count as already shipped. On a fixture with RPT0001 signed at the tag and RPT0002 signed and committed one commit after it, the cut exits 0 and records `"previous": "1.0.0-1-g5bf57365914310f532c0c2f448dadde644f426b3", "reports": []`, where the same fixture with an ordinary `v1.0.0` tag records `"previous": "v1.0.0", "reports": ["RPT0002"]`. The release's report is lost without a word, contrary to AC1's reports signed since the previous release and to changelog.d/US1233.md:7 "the nearest tag reachable from HEAD", and a re-cut keeps the wrong line byte for byte. No test covers a misnamed tag. Resolving the ref itself (for example `git show-ref --verify` of `refs/tags/<name>`, or listing tags merged into HEAD) would close it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** US1233 AC1 still passes: the cut records the version, its date and the reports signed since the previous release
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_the_cut_records_the_version_date_and_reports_since_the_last_release
- [ ] **AC3** US1233 AC2 still passes: a second cut of one version leaves one unchanged record
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_a_second_cut_of_one_version_leaves_one_unchanged_record
- [ ] **AC4** US1233 AC3 still passes: a first release with no signed report, no tag and no git is still recorded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_record.py::ReleaseRecordTests::test_a_release_with_no_signed_report_is_still_recorded

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Filed |
