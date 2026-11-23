# BG1540: US1173 is Done with AC3 verified, yet AC3 reads the live bug corpus and is red at HEAD

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, sdlc-studio/stories/US1173-v6-4-0-is-cut-version-changelog-known.md, changelog.d/BG1540.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, stories lens, survived 3 of 3 refute votes; observed at sdlc-studio/stories/US1173-v6-4-0-is-cut-version-changelog-known.md AC3 (lines 28-30) and Notes line 44
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:06Z

## Summary

AC3 of `sdlc-studio/stories/US1173-v6-4-0-is-cut-version-changelog-known.md` (lines 28 to 30) is verified by running the `bar` subcommand of `tools/known_issues.py`, which judges the bug corpus as it is today and not as it was at the cut. AC2 in the same story was deliberately pinned to the commit that cut 6.4.0 so a later filing does not turn it red (BG1054), but AC3 was left live, and the story's note (line 44) reasons only about the moment of a later cut. BG1507 (High) was filed after the tag, so the criterion of a Done story marked Verified yes now fails. The scheduled corpus-verify lane executes every Done story's Verify lines against `tools/verify-corpus-baseline.txt` and reddens on a count above it, so it gains a red criterion for a reason unrelated to this story's delivery. The release bar is a property of a tag and is already enforced where the tag is made; as a story criterion it is not a stable fact about the unit.

## Steps to Reproduce

1. From the repository root, run `tools/known_issues.py` with the `bar` subcommand.
2. Observe 'release bar NOT met: 1 open finding(s) at a barred severity - BG1507 (High)' and exit status 1.
3. Open the US1173 story file and read AC3 (lines 28 to 30): its Verify line is a shell run of that same command, and it is marked Verified yes on 2026-11-16 in a story whose Status is Done.
4. Read the Notes line beginning 'The criteria must stay true after later releases': AC2 is pinned to the cut commit and AC3 is said to read the live corpus.
5. Expected: a Done story's Verify lines stay green whatever is filed afterwards. Actual: any High finding filed between releases turns AC3 red.

## Proposed Fix

Give the `bar` subcommand of `tools/known_issues.py` an `--at` option that judges the corpus as it stood at a named commit, matching what the `check` subcommand already offers, with tests in `tools/tests/test_known_issues.py` for a High filed after that commit (bar met) and one open at it (bar not met). Repoint AC3's Verify line in the US1173 story file to judge the bar at the commit that cut 6.4.0, correct the Notes line that defends the live read, and record the change in the story's Revision History. Check the earlier release-cut stories for the same live Verify line and file each one found.

## Acceptance Criteria

- [ ] **AC1** Given a corpus in which a High bug was filed after commit C and none was open at C, when `tools/known_issues.py bar --at C` runs, then the bar is met and the exit status is 0. Fails on: a finding filed after a release turning that release's bar red.
  - **Verify:** pytest tools/tests/test_known_issues.py::ReleaseBarTests::test_a_high_filed_after_the_named_commit_does_not_break_the_bar_at_it
- [ ] **AC2** Given a corpus with a High bug open at commit C, when `bar --at C` runs, then the bar is not met, the bug is named and the exit status is non-zero; and `bar` with no `--at` still judges the working tree. Fails on: `--at` passing a finding that was open at the commit, or changing what the plain verb reads.
  - **Verify:** pytest tools/tests/test_known_issues.py::ReleaseBarTests::test_a_high_open_at_the_named_commit_still_breaks_the_bar
- [ ] **AC3** Given the US1173 story file after the fix, when AC3 is read, then its Verify line judges the bar at the commit that cut 6.4.0, the Notes line defending the live read is corrected, the Revision History records the change, and each earlier release-cut story found with the same live Verify line is filed. Fails on: a Done story whose criterion reddens when a High is filed between releases.
  - **Verify:** shell grep -A1 -E '^- [*][*]AC3:[*][*]' "$(ls sdlc-studio/stories/US1173-*.md)" | grep 'Verify:' | grep -q -- 'known_issues.py bar --at '

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-four orchestrator) | Run twenty-four goal review: AC3 had no Verify line. It now checks US1173's AC3 Verify judges the bar with --at. Fails at HEAD, where it reads the live corpus |
